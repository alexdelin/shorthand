import shlex
import logging
from subprocess import Popen, PIPE


log = logging.getLogger(__name__)


def search_notes(notes_directory, query_string, type=None,
                 case_sensitive=False, grep_path='grep'):
    '''Search through all notes and return
    matching lines with metadata

    "query_string" is a string of words which are searched for
        independently. However multi-word phrases can be searched
        for by quoting the phrase
    "type" is the type of objects to search (todos, questions, etc.)
    "case_sensitive" toggles whether or not the match is case
        sensitive
    '''

    query_components = shlex.split(query_string)

    # Early exit for empty query
    if not query_components:
        return []

    # Add safe handling of quoted phrases
    safe_components = []
    for component in query_components:
        if component[0] == '"' and component[-1] == '"':
            safe_components.append(component[1:-1])
        else:
            safe_components.append(component)

    grep_mode = '-rn'
    grep_filter_mode = ''
    if not case_sensitive:
        grep_mode += 'i'
        grep_filter_mode += ' -i'

    grep_command = '{grep_path} {mode} "{pattern}" {dir} | ' \
                   '{grep_path} -v "\\.git"'.format(
                        grep_path=grep_path,
                        mode=grep_mode,
                        pattern=query_components[0],
                        dir=notes_directory)

    for additional_filter in query_components[1:]:
        new_filter = ' | {grep_path}{mode} "{pattern}"'.format(
                        grep_path=grep_path,
                        mode=grep_filter_mode,
                        pattern=additional_filter)
        grep_command = grep_command + new_filter

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    search_results = []

    for line in output_lines:

        if not line.strip():
            continue

        split_line = line.split(':', 2)
        file_path = split_line[0].strip()
        line_number = split_line[1].strip()
        match_content = split_line[2].strip()

        # Return all paths as relative paths within the notes dir
        if notes_directory in file_path:
            file_path = file_path[len(notes_directory):]

        processed_line = {
            'file_path': file_path,
            'line_number': line_number,
            'match_content': match_content,
        }

        search_results.append(processed_line)

    return {
        "items": search_results,
        "count": len(search_results)
    }


def get_context(filename, line_number, width):
    '''Show the surrounding lines around a given line
    '''
    with open(filename, 'r') as file_object:
        file_content = file_object.read()

    split_content = file_content.split('\n')

    before_start = line_number - 1 - width
    if before_start < 0:
        before_start = 0
    before_end = line_number - 1
    before_content = split_content[before_start:before_end]

    line_content = split_content[line_number-1]

    after_start = line_number
    after_end = line_number + width
    if after_end > len(split_content):
        after_end = len(split_content)
    after_content = split_content[after_start:after_end]

    return {
        "before": before_content,
        "line": line_content,
        "after": after_content
    }


def get_note(path):

    with open(path, 'r') as note_file_object:
        note_content = note_file_object.read()

    return note_content
