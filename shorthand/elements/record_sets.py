from subprocess import Popen, PIPE
import logging

from shorthand.utils.patterns import RECORD_SET_PATTERN, escape_for_cli
from shorthand.utils.rec import load_from_string
from shorthand.utils.paths import get_relative_path, get_display_path, \
                                  get_full_path


log = logging.getLogger(__name__)


def _get_record_set(notes_directory, file_path, line_number, parse=True,
                    parse_format='json', include_config=False):
    '''Get the full contents of a record set
    If `parse` is set to False then the record set
        contents are returned as a string
    If `parse` is set to True then the record set
        contents are loaded and returned in the specified
        format. Valid formats are `json` and `csv`
    '''

    # Validate inputs
    if parse and parse_format not in ['json', 'csv']:
        raise ValueError(f'Unknown parse format {parse_format}')

    # Get full path if only a relative path is supplied
    if notes_directory not in file_path:
        file_path = get_full_path(notes_directory, file_path)

    record_set_lines = []
    is_content = False
    with open(file_path, 'r') as f:
        file_data = f.read()
    for idx, line in enumerate(file_data.split('\n')):
        if idx + 1 < line_number:
            continue
        elif idx + 1 == line_number and line != '```rec-data':
            raise ValueError(f'Found unexpected line "{line}"')
        elif idx + 1 == line_number and line == '```rec-data':
            is_content = True
        elif is_content and line != '```':
            record_set_lines.append(line)
            continue
        elif is_content and line == '```':
            is_content = False
            break
        else:
            raise ValueError('Found a bug in record set parsing logic!')
    record_set_raw = '\n'.join(record_set_lines)
    if parse:
        record_set = load_from_string(record_set_raw)
        if parse_format == 'json':
            if include_config:
                output = {
                    'records': list(record_set.all()),
                    'config': record_set.get_config(),
                    'fields': record_set.get_fields()
                }
                return output
            output = record_set.get_json()
            return output
        elif parse_format == 'csv':
            output = record_set.get_csv()
            return output
    else:
        return record_set_raw


def _get_record_sets(notes_directory, directory_filter=None, grep_path='grep'):
    '''List all record sets within a specified directory
    '''

    record_sets = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = '{grep_path} -Prn "{pattern}" '\
                   '--include="*.note" --exclude-dir=\'.*\' {dir}'.format(
                        grep_path=grep_path,
                        pattern=escape_for_cli(RECORD_SET_PATTERN),
                        dir=search_directory)

    log.debug(f'Running grep command {grep_command} to get record sets')

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

        file_path = get_relative_path(notes_directory, file_path)
        display_path = get_display_path(file_path, directory_filter)

        parsed_record_set = {
            "file_path": file_path,
            "line_number": line_number,
            "display_path": display_path
        }

        record_sets.append(parsed_record_set)

    return record_sets
