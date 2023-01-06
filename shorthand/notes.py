import re
import os
from subprocess import Popen, PIPE
import logging
from typing import Optional, TypedDict, cast, Union

from shorthand.utils.paths import get_full_path, get_relative_path, \
                                  parse_relative_link_path, is_external_path, \
                                  is_note_path
from shorthand.utils.patterns import INTERNAL_LINK_PATTERN, ALL_LINK_PATTERN
from shorthand.types import DirectoryPath, ExecutablePath, ExternalURL, NotePath, RawNoteContent, RelativeNotePath


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


def _get_note(notes_directory: DirectoryPath, path: NotePath
              ) -> RawNoteContent:
    '''Get the full raw content of a note as a string
    given:
        - The full path to the notes directory
        - Its path, as a relative path
          within the notes directory
    '''

    full_path = get_full_path(notes_directory, path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to get at path {path} does not exist')

    with open(full_path, 'r') as note_file_object:
        note_content = note_file_object.read()

    return note_content


def _update_note(notes_directory: DirectoryPath, file_path: NotePath,
                 content: RawNoteContent) -> None:
    '''Update an existing note with the full contents provided
    '''

    # Ensure that we have the full path even if
    # a relative path is specified
    full_path = get_full_path(notes_directory, file_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to get at path {file_path} does not exist')

    with open(full_path, 'w') as note_file:
        note_file.write(content)


def _append_to_note(notes_directory: DirectoryPath, note_path: NotePath,
                    content: RawNoteContent, blank_lines: int=1) -> None:
    '''Append the specified content to an existing note
    '''
    full_path = get_full_path(notes_directory, note_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to append to at path {note_path} does '
                         f'not exist')

    if blank_lines:
        content = ('\n' * (blank_lines + 1)) + content

    with open(full_path, 'a') as note_file:
        note_file.write(content)


def _create_note(notes_directory: DirectoryPath, note_path: NotePath,
                 content: Optional[RawNoteContent]=None) -> None:
    '''Create a new note
    '''
    if not note_path:
        raise ValueError('No note path provided for new note to create')

    full_path = get_full_path(notes_directory, note_path)

    if os.path.exists(full_path):
        raise ValueError(f'Note to create at path {note_path} already exists')

    with open(full_path, 'w') as f:
        if content:
            f.write(content)


def _delete_note(notes_directory: DirectoryPath, note_path: NotePath) -> None:
    '''Deletes a note from the filesystem
    '''
    full_path = get_full_path(notes_directory, note_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to delete at path {note_path} does not exist')

    os.remove(full_path)


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
    # Need to convert to a list of tuples to de-duplicate a
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
            raise ValueError('Parameter `note` cannot be combined '
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
    grep_command = '{grep_path} -Prn "{pattern}" '\
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
                is_valid_link = is_note_path(notes_directory, link_target_file)
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
