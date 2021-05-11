import re
import os
from subprocess import Popen, PIPE
import logging

from shorthand.utils.paths import get_full_path, get_relative_path, \
                                  parse_relative_link_path, is_external_path
from shorthand.utils.patterns import INTERNAL_LINK_PATTERN, ALL_LINK_PATTERN


link_regex = re.compile(ALL_LINK_PATTERN)
internal_link_regex = re.compile(INTERNAL_LINK_PATTERN)


log = logging.getLogger(__name__)


def _get_note(notes_directory, path):
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


def _update_note(notes_directory, file_path, content):
    '''Update an existing note with the full contents provided
    '''

    # Ensure that we have the full path even if
    # a relative path is specified
    full_path = get_full_path(notes_directory, file_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to get at path {file_path} does not exist')

    with open(full_path, 'w') as note_file:
        note_file.write(content)


def _append_to_note(notes_directory, note_path, content, blank_lines=1):
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


def _create_note(notes_directory, note_path, content=None):
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


def _delete_note(notes_directory, note_path):
    '''Deletes a note from the filesystem
    '''
    full_path = get_full_path(notes_directory, note_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Note to delete at path {note_path} does not exist')

    os.remove(full_path)


def _validate_internal_links(notes_directory, grep_path='grep'):
    '''Validate that all of the internal links within notes point
       to files that actually exist within the notes directory (not
           necessarily other notes files)
    '''

    invalid_links = []

    # Use Grep to find all internal links
    grep_command = '{grep_path} -Prn "{pattern}" '\
                   '--include="*.note" {dir}'.format(
                        grep_path=grep_path,
                        pattern=INTERNAL_LINK_PATTERN,
                        dir=notes_directory)
    log.debug(f'Running grep command {grep_command} to get internal links')

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

        split_line = line.split(':', 2)

        file_path = split_line[0].strip()
        line_number = split_line[1].strip()
        match_content = split_line[2].strip()

        note_path = get_relative_path(notes_directory, file_path)

        matches = internal_link_regex.findall(match_content)
        for match in matches:
            # The matching group for the text starts
            # with `[` and ends with `](`
            link_text = match[0][1:-2]
            link_target = match[1]
            log.debug(match)

            # Handle absolute paths within the notes directory
            if link_target[0] == '/':
                link_full_target = get_full_path(notes_directory, link_target)

            # Handle relative paths from the source note
            else:
                link_target = parse_relative_link_path(source=note_path,
                                                       target=link_target)
                link_full_target = get_full_path(notes_directory, link_target)

            if not os.path.exists(link_full_target):
                link = {
                    'line_number': line_number,
                    'source': note_path,
                    'target': link_target,
                    'text': link_text
                }
                invalid_links.append(link)

    return invalid_links


def _get_backlinks(notes_directory, note_path, grep_path='grep'):
    '''Get backlinks from various notes to the specified note
    '''
    return _get_links(notes_directory=notes_directory, target=note_path,
                      include_external=False, include_invalid=False,
                      grep_path=grep_path)


def _get_links(notes_directory, source=None, target=None,
               include_external=False, include_invalid=False,
               grep_path='grep'):
    '''Get all links between notes within the notes directory
    '''

    links = []

    if target:
        target_filename = os.path.basename(target)

    LINK_PATTERN = r'(\[)([^\[]*?)(\]\()'
    if target:
        # Only include the target filename to catch both
        # relative and absolute references
        LINK_PATTERN += rf'(.*?{target_filename})'
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
                   '--include="*.note" {dir}'.format(
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

            if target and link_target != target:
                log.debug(f'Found unexpected target {link_target}')
                continue

            if not include_external and (is_external_path(link_target)):
                continue

            log.debug(match)

            # Only check that targets of internal links
            # actually exist (if we need to)
            if not is_external_path(link_target):
                link_full_target = get_full_path(notes_directory, link_target)
                if not include_invalid:
                    if not os.path.exists(link_full_target):
                        log.info(f'Skipping invalid link to {link_target}')
                        continue

            link = {
                'line_number': line_number,
                'source': note_path,
                'target': link_target,
                'text': link_text
            }

            links.append(link)

    return links
