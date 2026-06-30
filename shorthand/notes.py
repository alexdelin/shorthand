import difflib
import re
import os
from subprocess import Popen, PIPE
import logging
from typing import Optional, TypedDict, cast, Union
from datetime import UTC, datetime

from shorthand.utils import do_atomic_file_update
from shorthand.utils.paths import get_full_path, get_relative_path, \
                                  parse_relative_link_path, is_external_path, \
                                  _is_note_path
from shorthand.utils.patterns import INTERNAL_LINK_PATTERN, ALL_LINK_PATTERN
from shorthand.types import DirectoryPath, ExecutablePath, ExternalURL, NoteContentAsOfTime, NoteLastModTime, NotePath, RawNoteContent, RelativeNotePath


link_regex = re.compile(ALL_LINK_PATTERN)
internal_link_regex = re.compile(INTERNAL_LINK_PATTERN)


log = logging.getLogger(__name__)


class Link(TypedDict):
    line_number: str
    source: NotePath
    target: Union[NotePath, RelativeNotePath, ExternalURL]
    text: str
    internal: bool
    valid: bool


def get_last_mod_time(notes_directory: DirectoryPath, path: NotePath
                      ) -> NoteLastModTime:
    '''Get the Version ID for a note stored on the filesystem
    '''
    full_path = get_full_path(notes_directory, path)
    m_timestamp = os.path.getmtime(full_path)
    m_datetime = datetime.fromtimestamp(m_timestamp, tz=UTC)
    m_time_string = m_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
    return m_time_string


def _get_note(notes_directory: DirectoryPath, path: NotePath
              ) -> RawNoteContent:
    '''Get the full raw content of a note as a string
    given:
        - The full path to the notes directory
        - Its path, as a relative path
          within the notes directory
    '''

    if not _is_note_path(notes_directory, path, must_exist=True):
        raise ValueError(f'Valid note not found at path {path}')

    full_path = get_full_path(notes_directory, path)
    with open(full_path, 'r') as note_file_object:
        note_content = note_file_object.read()

    return note_content


def _get_note_with_last_mod_time(notes_directory: DirectoryPath,
                                 path: NotePath) -> NoteContentAsOfTime:

    note_content = _get_note(notes_directory, path)
    last_mod_time = get_last_mod_time(notes_directory, path)

    return {
        "last_mod_time": last_mod_time,
        "content": note_content
    }


class UpdateNoteResult(TypedDict):
    update_made: bool
    incremental_diff: str
    new_last_mod_time: Optional[NoteLastModTime]


def _update_note(notes_directory: DirectoryPath, file_path: NotePath,
                 content: RawNoteContent,
                 starting_version_last_mod_time: Optional[NoteLastModTime] = None,
                 force_update: bool = False) -> UpdateNoteResult:
    ''' Update an existing note with the full contents provided.
        If a last_mod_time is provided for the starting version used in the
        editing session, it must match the last mod time of the current
        version in the notes directory. To ignore this requirement the
        update can be forced

        Takes the following arguments:
            `notes_directory`: String - Absolute path to the notes directory
            `file_path`: String - Relative path to the note being updated
            `content`: String - New content to update the file with
            `starting_version_last_mod_time`: String | None - Last modified
                time of the version of the file that the edit session was
                last refreshed with
            `force_update`: Boolean - Whether to force the update

        Returns a dictionary with the following keys:
            `update_made`: Boolean - Whether an update was made or not
            `incremental_diff`: String - The incremental diff of the change
                which was made by the update, or would have been made by the
                update if it was not performed
            `new_last_mod_time`: String | None - If the update was performed,
                the new last modified time of the updated note on disk
    '''

    # Ensure that we have the full path even if
    # a relative path is specified
    full_path = get_full_path(notes_directory, file_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to get at path {file_path} does not exist')

    current_content = _get_note(notes_directory, file_path)
    if current_content == content:
        incremental_diff = ''
    else:
        diff_lines = list(difflib.unified_diff(
            current_content.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f'{file_path} (old)',
            tofile=f'{file_path} (new)',
            lineterm='\n'))
        cleaned_diff_lines = []
        for line in diff_lines:
            if line.endswith('\n'):
                cleaned_diff_lines.append(line)
            else:
                cleaned_diff_lines.append(line + '\n')

        incremental_diff = ''.join(cleaned_diff_lines)

    stored_last_mod_time = get_last_mod_time(notes_directory, file_path)

    if force_update or (not starting_version_last_mod_time) or (stored_last_mod_time == starting_version_last_mod_time):

        if force_update:
            log.warning(f'Forcing update to note {file_path}')

        do_atomic_file_update(full_path, content, notes_directory)

        new_last_mod_time = get_last_mod_time(notes_directory, file_path)

        return {
            'update_made': True,
            'incremental_diff': incremental_diff,
            'new_last_mod_time': new_last_mod_time
        }

    else:
        return {
            'update_made': False,
            'incremental_diff': incremental_diff,
            'new_last_mod_time': None
        }


def _append_to_note(notes_directory: DirectoryPath, note_path: NotePath,
                    content: RawNoteContent, blank_lines: int = 1) -> None:
    '''Append the specified content to an existing note
    '''
    full_path = get_full_path(notes_directory, note_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to append to at path {note_path} does ' +
                         f'not exist')

    if blank_lines:
        content = ('\n' * (blank_lines + 1)) + content

    with open(full_path, 'a') as note_file:
        note_file.write(content)


def _validate_internal_links(notes_directory: DirectoryPath,
                             source: Optional[NotePath]=None,
                             grep_path: ExecutablePath='grep'
                             ) -> list[Link]:
    '''Validate that all of the internal links within notes point
       to files that actually exist within the notes directory (not
           necessarily other notes files)

       Returns a list of all links with invalid targets
    '''

    all_internal_links = _get_links(notes_directory=notes_directory,
                                    source=source, target=None, note=None,
                                    include_external=False,
                                    include_invalid=True,
                                    grep_path=grep_path)
    invalid_links = [link for link in all_internal_links if not link['valid']]

    return invalid_links


def deduplicate_links(links: list[Link]) -> list[Link]:
    # Need to convert to a set of tuples to de-duplicate a
    # list of dictionaries
    unique_tuples = set([tuple(item.items()) for item in links])
    return [cast(Link, dict(tupleized)) for tupleized in unique_tuples]


def _get_backlinks(notes_directory: DirectoryPath, note_path: NotePath,
                   grep_path: ExecutablePath='grep') -> list[Link]:
    '''Get backlinks from various notes to the specified note
    '''
    return _get_links(notes_directory=notes_directory, target=note_path,
                      include_external=False, include_invalid=False,
                      grep_path=grep_path)


def _get_links(notes_directory: DirectoryPath, source: Optional[NotePath]=None,
               target: Optional[NotePath]=None, note: Optional[NotePath]=None,
               include_external: bool=False, include_invalid: bool=False,
               grep_path: ExecutablePath='grep') -> list[Link]:
    '''Get all links between notes within the notes directory

       notes_directory: The directory to do the search within
       source: Only return links where the specified note is the source of
               the link
       target: Only return links where the specified note is the target of
               the link
       note: Only return links where the specified note is either the source or
             the target of the link
       include_external: Boolean for whether or not external links are included
       include_invalid: Boolean for whether or not links with invlaid targets
                        are included
       grep_path: Path to the grep CLI utility to use for the search

       Returns:
            [
                {
                    'line_number': '26',
                    'source': '/section/mixed.note',
                    'target': '/todos.note',
                    'text': 'todos',
                    'internal': true,
                    'valid': true
                }, {
                    'line_number': '26',
                    'source': '/section/mixed.note',
                    'target': '/questions.note',
                    'text': 'questions',
                    'internal': true,
                    'valid': true
                }
            ]
    '''

    if note:
        if source or target:
            raise ValueError('Parameter `note` cannot be combined ' +
                             'with `source` or `target`')

        # Get the set of all links where the specified note is either
        # the source or the target
        source_links = _get_links(notes_directory=notes_directory, source=note,
                                  target=None, note=None,
                                  include_external=include_external,
                                  include_invalid=include_invalid,
                                  grep_path=grep_path)
        target_links = _get_links(notes_directory=notes_directory, source=None,
                                  target=note, note=None,
                                  include_external=include_external,
                                  include_invalid=include_invalid,
                                  grep_path=grep_path)

        all_links = source_links + target_links
        all_links = deduplicate_links(all_links)

        return all_links

    links = []

    LINK_PATTERN = r'(\[)([^\[]*?)(\]\()'
    if target:
        # Only include the target filename to catch both
        # relative and absolute references
        target_filename = os.path.basename(target)
        LINK_PATTERN += rf'(.*?{target_filename})(#.+?)?'
    elif not include_external:
        # Only catch internal links which don't have http[s]://
        LINK_PATTERN += r'((?!(https://|http://)).*?)'
    else:
        # Catch everything
        LINK_PATTERN += r'(.*?)'
    LINK_PATTERN += r'(\))'

    if source:
        search_path = get_full_path(notes_directory, source)
    else:
        search_path = notes_directory

    # Use Grep to find all links
    grep_command = '{grep_path} -Prn "{pattern}" ' \
                   '--include="*.note" --exclude-dir=\'.*\' {dir}'.format(
                        grep_path=grep_path,
                        pattern=LINK_PATTERN,
                        dir=search_path)
    log.debug(f'Running grep command {grep_command} to get links')

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    for line in output_lines:

        log.debug(f'Got line "{line}"')

        if not line.strip():
            continue

        # Grep returns results in different forms depending on if you specify
        # a path to a file or directory
        #     dir:  <file-path>:<line-number>:<line>
        #     file: <line-number>:<line>
        if source:
            split_line = line.split(':', 1)

            file_path = source
            line_number = split_line[0].strip()
            match_content = split_line[1].strip()

        else:
            split_line = line.split(':', 2)

            file_path = split_line[0].strip()
            line_number = split_line[1].strip()
            match_content = split_line[2].strip()

        note_path = get_relative_path(notes_directory, file_path)

        matches = link_regex.findall(match_content)
        for match in matches:

            # The matching group for the text starts
            # with `[` and ends with `](`
            link_text = match[0][1:-2]
            link_target = match[1]

            link_target = parse_relative_link_path(source=note_path,
                                                   target=link_target)
            link_target_file = link_target.split('#')[0]
            is_external_link = False
            is_valid_link = True

            # Sanity check the link target which Grep should have already
            # filtered for
            if target and link_target != target:
                if '#' in link_target and link_target_file == target:
                    log.debug(f'Found link to subsection {link_target}')
                else:
                    log.debug(f'Found unexpected target {link_target}')
                    continue

            is_external_link = is_external_path(link_target)
            if is_external_link and not include_external:
                continue

            if not is_external_link:
                is_valid_link = _is_note_path(notes_directory, link_target_file)
                if not include_invalid and not is_valid_link:
                    log.info(f'Skipping invalid link to {link_target}')
                    continue

            link = {
                'line_number': line_number,
                'source': note_path,
                'target': link_target,
                'text': link_text,
                'internal': not is_external_link,
                'valid': is_valid_link
            }

            links.append(link)

    return links
