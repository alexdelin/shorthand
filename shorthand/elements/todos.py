import re
import logging
from datetime import datetime
from subprocess import Popen, PIPE
import shlex

from shorthand.tags import extract_tags
from shorthand.utils.paths import get_relative_path, get_display_path, \
                                  get_full_path
from shorthand.utils.patterns import INCOMPLETE_PREFIX_GREP, \
    COMPLETE_PREFIX_GREP, SKIPPED_PREFIX_GREP, \
    START_STAMP_ONLY_PATTERN, START_END_STAMP_ONLY_PATTERN

# Set up Regexes to use for finding files to process with `grep`
PATTERN_MAPPING = {
    'incomplete': INCOMPLETE_PREFIX_GREP,
    'complete': COMPLETE_PREFIX_GREP,
    'skipped': SKIPPED_PREFIX_GREP
}

SUPPORTED_SORT_FIELDS = ['start_date']


log = logging.getLogger(__name__)


def parse_todo(todo_line):
    '''A standalone parser for a single line todo element
    '''

    # remove the leading `[]`, `[ ]`, `[X]`, or `[S]`
    todo_content = todo_line.split(']', 1)[1].strip()
    status_marker = todo_line.split(']', 1)[0].split('[')[1].strip()
    if status_marker == 'X':
        todo_status = 'complete'
    elif status_marker == 'S':
        todo_status = 'skipped'
    else:
        todo_status = 'incomplete'

    # Pull out and structure out date info if included
    start_stamp_regex = re.compile(START_STAMP_ONLY_PATTERN)
    start_end_stamp_regex = re.compile(START_END_STAMP_ONLY_PATTERN)

    start_stamp_match = start_stamp_regex.match(todo_content)
    start_end_stamp_match = start_end_stamp_regex.match(todo_content)
    if start_stamp_match:
        start_date = start_stamp_match.groups()[1]
        end_date = None
        todo_text = start_stamp_match.groups()[4]
    elif start_end_stamp_match:
        start_date = start_end_stamp_match.groups()[1]
        end_date = start_end_stamp_match.groups()[3]
        todo_text = start_end_stamp_match.groups()[6]
    else:
        start_date = None
        end_date = None
        todo_text = todo_content

    tags, clean_text = extract_tags(todo_text)
    if tags:
        todo_text = clean_text

    processed_todo = {
            'todo_text': todo_text,
            'start_date': start_date,
            'end_date': end_date,
            'status': todo_status,
            'tags': tags
        }

    return processed_todo


def _get_todos(notes_directory, todo_status='incomplete',
               directory_filter=None, query_string=None, case_sensitive=False,
               sort_by=None, suppress_future=True, tag=None,
               grep_path='grep'):
    '''Get a specified set of todos using grep on the filesystem
    '''

    log.info(f'Getting {todo_status} todos in directory {directory_filter}'
             f' with query string "{query_string}" sorted by {sort_by}')

    todo_status = todo_status.lower()

    if todo_status not in PATTERN_MAPPING.keys():
        log.error(f'Got invalid todo type {todo_status}')
        raise ValueError(f'Invalid todo type {todo_status} specified. '
                         f'Valid options are: '
                         f'{", ".join(PATTERN_MAPPING.keys())}')

    todo_items = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = '{grep_path} -Prn "{pattern}" '\
                   '--include="*.note" {dir}'.format(
                        grep_path=grep_path,
                        pattern=PATTERN_MAPPING[todo_status],
                        dir=search_directory)

    if query_string:
        query_components = shlex.split(query_string)
        # Add safe handling of quoted phrases
        safe_components = []
        for component in query_components:
            if component[0] == '"' and component[-1] == '"':
                safe_components.append(component[1:-1])
            else:
                safe_components.append(component)

        if not case_sensitive:
            grep_filter_mode = ' -i'
        else:
            grep_filter_mode = ''

        for additional_filter in query_components:
            new_filter = ' | {grep_path}{mode} "{pattern}"'.format(
                            grep_path=grep_path,
                            mode=grep_filter_mode,
                            pattern=additional_filter)
            grep_command = grep_command + new_filter

    if tag:
        new_filter = f' | {grep_path} ":{tag}:"'
        grep_command = grep_command + new_filter

    log.debug(f'Running grep command {grep_command} to get todos')
    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    start_stamp_regex = re.compile(START_STAMP_ONLY_PATTERN)
    start_end_stamp_regex = re.compile(START_END_STAMP_ONLY_PATTERN)

    for line in output_lines:

        if not line.strip():
            continue

        split_line = line.split(':', 2)
        file_path = split_line[0].strip()
        line_number = split_line[1].strip()
        match_content = split_line[2].strip()

        # remove the leading `[]`, `[ ]`, `[X]`, or `[S]`
        match_content = match_content.split(']', 1)[1].strip()

        # Return all paths as relative paths within the notes dir
        file_path = get_relative_path(notes_directory, file_path)

        # Pull out and structure out date info if included
        start_stamp_match = start_stamp_regex.match(match_content)
        start_end_stamp_match = start_end_stamp_regex.match(match_content)
        if start_stamp_match:
            start_date = start_stamp_match.groups()[1]
            end_date = None
            todo_text = start_stamp_match.groups()[4]
        elif start_end_stamp_match:
            start_date = start_end_stamp_match.groups()[1]
            end_date = start_end_stamp_match.groups()[3]
            todo_text = start_end_stamp_match.groups()[6]
        else:
            start_date = None
            end_date = None
            todo_text = match_content

        tags, clean_text = extract_tags(todo_text)
        if tags:
            todo_text = clean_text

        display_path = get_display_path(file_path, directory_filter)

        processed_todo = {
            'file_path': file_path,
            'display_path': display_path,
            'line_number': line_number,
            'todo_text': todo_text,
            'start_date': start_date,
            'end_date': end_date,
            'status': todo_status,
            'tags': tags
        }

        is_future_todo = False
        current_date_stamp = datetime.now().isoformat()[:10]
        if start_date:
            if start_date > current_date_stamp:
                is_future_todo = True

        if not suppress_future or not is_future_todo:
            todo_items.append(processed_todo)

    # Sort Results
    if sort_by:
        if sort_by not in SUPPORTED_SORT_FIELDS:
            raise ValueError('Invalid sort field {}'.format(sort_by))
        todo_items = sorted(todo_items,
                            key=lambda k: k[sort_by] if k[sort_by] else '',
                            reverse=True)

    # Wrap Results
    log.info(f'returning {len(todo_items)} todos')
    return todo_items


def analyze_todos(todos):
    '''Analyze todos and generate basic statistics
    '''

    # Aggregate and count tags
    tag_counts = {}
    for todo in todos:
        for tag in todo.get('tags', []):
            if tag not in tag_counts.keys():
                tag_counts[tag] = 1
            else:
                tag_counts[tag] += 1

    # Aggregate and count months
    month_counts = {}
    for todo in todos:
        date = todo.get('start_date')
        if not date:
            continue
        month = date[:7]
        if month not in month_counts.keys():
            month_counts[month] = 1
        else:
            month_counts[month] += 1

    # Make dataset for timeline
    timeline_data = []
    for month_string, month_count in month_counts.items():
        timeline_data.append([
            int(datetime.strptime(
                f'{month_string}-01T12:00:00',
                '%Y-%m-%dT%H:%M:%S').strftime("%s")) * 1000,
            month_count
        ])

    # Aggregate and count subdirectories

    return {
        'tag_counts': tag_counts,
        'month_counts': month_counts,
        'timeline_data': timeline_data
    }


def _mark_todo(notes_directory, note_path, line_number, status):

    full_path = get_full_path(notes_directory, note_path)

    with open(full_path, 'r') as file_object:
        file_content = file_object.read()

    split_content = file_content.split('\n')
    line_content = split_content[line_number-1]

    # Modify line_content
    block_pattern = r'(^\s*)(\[)([ XS]*)(\])'
    block_regex = re.compile(block_pattern)

    if status == 'complete':
        sub_character = 'X'
    elif status == 'skipped':
        sub_character = 'S'
    else:
        sub_character = ' '

    line_content = block_regex.sub(
        '\\g<1>[{}]'.format(sub_character),
        line_content)

    split_content[line_number-1] = line_content
    with open(full_path, 'w') as file_object:
        file_object.write('\n'.join(split_content))

    return line_content
