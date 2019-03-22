import re
from subprocess import Popen, PIPE
from note_parser.utils.patterns import INCOMPLETE_PREFIX_GREP, \
                    COMPLETE_PREFIX_GREP, SKIPPED_PREFIX_GREP

# Set up Regexes to use for finding files to process with `grep`
PATTERN_MAPPING = {
    'incomplete': INCOMPLETE_PREFIX_GREP,
    'complete': COMPLETE_PREFIX_GREP,
    'skipped': SKIPPED_PREFIX_GREP
}


def get_todos(todo_status='incomplete'):

    if todo_status not in PATTERN_MAPPING.keys():
        raise ValueError('Invalid todo type ' + todo_status)

    todo_items = []

    proc = Popen(
        'grep -rn {pattern} .'.format(
            pattern=PATTERN_MAPPING[todo_status]),
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


mark_todo('test.note', 36, 'skipped')
