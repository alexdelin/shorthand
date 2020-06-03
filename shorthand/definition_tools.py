import re
from datetime import datetime
from subprocess import Popen, PIPE
import shlex
import logging

from shorthand.utils.patterns import DEFINITION_PATTERN, DEFINITION_GREP
from shorthand.utils.paths import get_relative_path, get_display_path


definition_regex = re.compile(DEFINITION_PATTERN)


log = logging.getLogger(__name__)


def get_definitions(notes_directory, directory_filter=None, grep_path='grep'):

    definitions = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = '{grep_path} -rn "{pattern}" {dir} | {grep_path} -v "\\.git"'.format(
            grep_path=grep_path,
            pattern=DEFINITION_GREP,
            dir=search_directory)

    log.debug(f'Running grep command {grep_command} to get definitions')
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
        file_path = split_line[0]
        line_number = split_line[1]
        definition_raw = split_line[2]

        # Return all paths as relative paths within the notes dir
        file_path = get_relative_path(notes_directory, file_path)
        display_path = get_display_path(file_path, directory_filter)

        definition_match = definition_regex.match(definition_raw)
        if not definition_match:
            log.debug(f'No definition match found for line {line}')
        else:
            term = definition_match.group(2)
            term = term.strip().strip('{}')
            definition_text = definition_match.group(3)

        parsed_definition = {
            "file_path": file_path,
            "display_path": display_path,
            "line_number": line_number,
            "term": term,
            "definition": definition_text
        }

        definitions.append(parsed_definition)

    return definitions
