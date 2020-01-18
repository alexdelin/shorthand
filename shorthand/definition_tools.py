import re
from datetime import datetime
from subprocess import Popen, PIPE
import shlex

from shorthand.utils.patterns import DEFINITION_PATTERN, escape_for_grep


definition_regex = re.compile(DEFINITION_PATTERN)


def get_definitions(notes_directory, directory_filter=None):

    definitions = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = 'grep -rn "{pattern}" {dir} | grep -v "\\.git"'.format(
            pattern=escape_for_grep(DEFINITION_PATTERN),
            dir=search_directory)

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

        definition_match = definition_regex.match(definition_raw)
        if not definition_match:
            print('NO MATCH FOUND?!?!')
        else:
            term = definition_match.group(2)
            term = term.strip().strip('{}')
            definition_text = definition_match.group(3)

        parsed_definition = {
            "file_path": file_path,
            "line_number": line_number,
            "term": term,
            "definition": definition_text
        }

        definitions.append(parsed_definition)

    return definitions
