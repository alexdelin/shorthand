import re
from subprocess import Popen, PIPE
import logging
from typing import List, Optional, TypedDict, Required
from shorthand.types import DirectoryPath, DisplayPath, ExecutablePath, RelativeDirectoryPath, RelativeNotePath

from shorthand.utils.patterns import DEFINITION_PATTERN
from shorthand.utils.paths import get_full_path, get_relative_path, get_display_path


definition_regex = re.compile(DEFINITION_PATTERN)


log = logging.getLogger(__name__)


class Definition(TypedDict, total=False):
    file_path: Required[RelativeNotePath]
    display_path: Required[DisplayPath]
    line_number: Required[str]
    term: Required[str]
    definition: Required[str]
    sub_elements: str


def _get_definitions(notes_directory: DirectoryPath,
                     directory_filter: Optional[RelativeDirectoryPath] = None,
                     grep_path: ExecutablePath = 'grep',
                     include_sub_elements: bool = False) -> List[Definition]:

    definitions: List[Definition] = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = '{grep_path} -Prn "{pattern}" '\
                   '--include="*.note" {dir}'.format(
                        grep_path=grep_path,
                        pattern=DEFINITION_PATTERN,
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
        # Placeholders
        term = ''
        definition_text = ''

        definition_match = definition_regex.match(definition_raw)
        if not definition_match:
            log.debug(f'No definition match found for line {line}')
        else:
            term = definition_match.group(3)
            term = term.strip().strip(r'{}')
            definition_text = definition_match.group(4)

        parsed_definition: Definition = {
            "file_path": file_path,
            "display_path": display_path,
            "line_number": line_number,
            "term": term,
            "definition": definition_text
        }

        if include_sub_elements:
            full_file_path = get_full_path(notes_directory, file_path)
            indent_level = 0
            sub_element_lines = []
            with open(full_file_path, 'r') as f:
                file_contents = f.read()
            for line_num, line_content in enumerate(file_contents.split('\n')):
                if line_num + 1 < int(line_number):
                    continue
                elif line_num + 1 == int(line_number):
                    indent_level = len(line_content) - len(line_content.lstrip(' '))
                elif line_num + 1 > int(line_number):
                    current_indent = len(line_content) - len(line_content.lstrip(' '))
                    if current_indent > indent_level:
                        sub_element_lines.append(line_content)
                    else:
                        break

            parsed_definition['sub_elements'] = '\n'.join(sub_element_lines)

        definitions.append(parsed_definition)

    return definitions
