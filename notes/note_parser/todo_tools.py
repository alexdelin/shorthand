import re
from datetime import datetime
from subprocess import Popen, PIPE

from note_parser.utils.patterns import INCOMPLETE_PREFIX_GREP, \
    COMPLETE_PREFIX_GREP, SKIPPED_PREFIX_GREP, CATCH_ALL_PATTERN, \
    VALID_INCOMPLETE_PATTERN, VALID_COMPLETE_PATTERN, \
    UNFINISHED_UNSTAMPED_PATTERN, FINISHED_START_STAMPED_PATTERN, \
    FINISHED_UNSTAMPED_PATTERN

# Set up Regexes to use for finding files to process with `grep`
PATTERN_MAPPING = {
    'incomplete': INCOMPLETE_PREFIX_GREP,
    'complete': COMPLETE_PREFIX_GREP,
    'skipped': SKIPPED_PREFIX_GREP
}


def stamp_notes(notes_directory):

    grep_command = 'grep -r {pattern} {directory} | '\
                   'grep -v {filter_1} | '\
                   'grep -v {filter_2}'.format(
                        pattern=CATCH_ALL_PATTERN,
                        directory=notes_directory,
                        filter_1=VALID_INCOMPLETE_PATTERN,
                        filter_2=VALID_COMPLETE_PATTERN)

    proc = Popen(grep_command,
                 stdout=PIPE, stderr=PIPE,
                 shell=True)
    output, err = proc.communicate()

    output_lines = output.split('\n')
    matched_filenames = [line.split(':')[0] for line in output_lines if line.strip()]
    matched_filenames = list(set(matched_filenames))

    # Compile regexes for replacing lines
    unfinished_unstamped_regex = re.compile(UNFINISHED_UNSTAMPED_PATTERN)
    finished_start_stamped_regex = re.compile(FINISHED_START_STAMPED_PATTERN)
    finished_unstamped_regex = re.compile(FINISHED_UNSTAMPED_PATTERN)

    for filename in matched_filenames:
        print(filename)
        with open(filename, 'r') as file_object:

            stamped_content = []

            for line in file_object:

                if unfinished_unstamped_regex.match(line):
                    # unfinished unstamped
                    print(line.rstrip())
                    line = unfinished_unstamped_regex.sub(
                        '\\g<1>[ ] ({timestamp}) '.format(
                            timestamp=datetime.now().isoformat()[:10]),
                        line)
                    print(line.rstrip())
                    stamped_content.append(line)
                elif finished_start_stamped_regex.match(line):
                    # finished with start stamped
                    print(line.rstrip())
                    line = finished_start_stamped_regex.sub(
                        '\\g<1>[\\g<3>] (\\g<6> -> {timestamp_2}) '.format(
                            timestamp_2=datetime.now().isoformat()[:10]),
                        line)
                    print(line.rstrip())
                    stamped_content.append(line)
                elif finished_unstamped_regex.match(line):
                    # finished unstamped
                    print(line.rstrip())
                    line = finished_unstamped_regex.sub(
                        '\\g<1>[\\g<3>] ({timestamp} -> {timestamp}) '.format(
                            timestamp=datetime.now().isoformat()[:10]),
                        line)
                    print(line.rstrip())
                    stamped_content.append(line)
                else:
                    # no to-dos -or- correctly formatted already
                    stamped_content.append(line)

        with open(filename, 'w') as write_file_object:
            write_file_object.write(''.join(stamped_content))

    return 'Done!'


def get_todos(notes_directory, todo_status='incomplete'):

    if todo_status not in PATTERN_MAPPING.keys():
        raise ValueError('Invalid todo type ' + todo_status)

    todo_items = []

    proc = Popen(
        'grep -rn {pattern} {dir}'.format(
            pattern=PATTERN_MAPPING[todo_status],
            dir=notes_directory),
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.split('\n')

    for line in output_lines:

        if not line.strip():
            continue

        split_line = line.split(':', 2)
        file_path = split_line[0].strip()
        line_number = split_line[1].strip()
        match_content = split_line[2].strip()

        # remove the leading `[]`, `[ ]`, `[X]`, or `[S]`
        match_content = match_content.split(']', 1)[1]

        processed_todo = {
            'file_path': file_path,
            'line_number': line_number,
            'match_content': match_content,
            'status': todo_status
        }

        todo_items.append(processed_todo)

    return todo_items


def mark_todo(filename, line_number, status):

    with open(filename, 'r') as file_object:
        file_content = file_object.read()

    split_content = file_content.split('\n')
    line_content = split_content[line_number-1]
    print(line_content)

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

    print(line_content)
    split_content[line_number-1] = line_content
    with open(filename, 'w') as file_object:
        file_object.write('\n'.join(split_content))

    return line_content
