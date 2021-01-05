import re
import os
from subprocess import Popen, PIPE
import logging

from shorthand.utils.paths import get_full_path, get_relative_path
from shorthand.utils.patterns import INTERNAL_LINK_PATTERN


link_regex = re.compile(INTERNAL_LINK_PATTERN)


log = logging.getLogger(__name__)


def _get_note(notes_directory, path):
    '''Get the full raw content of a note as a string
    given:
        - The full path to the notes directory
        - Its path, as a relative path
          within the notes directory
    '''

    full_path = get_full_path(notes_directory, path)

    with open(full_path, 'r') as note_file_object:
        note_content = note_file_object.read()

    return note_content


def _update_note(notes_directory, file_path, content):
    '''Update an existing note with the full contents provided
    '''

    # Ensure that we have the full path even if
    # a relative path is specified
    full_path = get_full_path(notes_directory, file_path)

    with open(full_path, 'w') as note_file:
        note_file.write(content)


def _append_to_note():
    '''Append the specified content to an existing note
    '''
    raise NotImplementedError('Not implemented yet!')


def _create_note():
    '''Create a new note
    '''
    raise NotImplementedError('Not implemented yet!')


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

        if not line.strip():
            continue

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
            link_full_target = get_full_path(notes_directory, link_target)
            if not os.path.exists(link_full_target):
                link = {
                    'line_number': line_number,
                    'path': note_path,
                    'link_target': link_target,
                    'link_text': link_text
                }
                invalid_links.append(link)

    return invalid_links
