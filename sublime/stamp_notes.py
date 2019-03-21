import re
from datetime import datetime
from subprocess import Popen, PIPE

# Set up Regexes to use for finding files to process with `grep`
catch_all_pattern = r'"\(^\\s*\)\(\[ \]\|\[\]\|\[X\]\|\[S\]\)"'
valid_incomplete_pattern = r'"\[ \] ([1-2]\\d\{3\}-\\d\{2\}-\\d\{2\})"'
valid_complete_pattern = r'"\[[XS]\] ([1-2]\\d\{3\}-\\d\{2\}-\\d\{2\} -> [1-2]\\d\{3\}-\\d\{2\}-\\d\{2\})"'

proc = Popen(
    'grep -r {pattern} . | grep -v {filter_1} | grep -v {filter_2}'.format(
        pattern=catch_all_pattern,
        filter_1=valid_incomplete_pattern,
        filter_2=valid_complete_pattern),
    stdout=PIPE, stderr=PIPE,
    shell=True)
output, err = proc.communicate()
output_lines = output.split('\n')
matched_filenames = [line.split(':')[0] for line in output_lines if line.strip()]
matched_filenames = list(set(matched_filenames))


# Compile regexes for replacing lines
unfinished_unstamped_pattern = r'(^\s*)(\[ \]|\[\]) (?!\([1-2]\d{3}\-\d{2}\-\d{2}\))'
unfinished_unstamped_regex = re.compile(unfinished_unstamped_pattern)

finished_start_stamped_pattern = r'(^\s*)(\[)([XS])(\] )(\()([1-2]\d{3}\-\d{2}\-\d{2})(\)) '
finished_start_stamped_regex = re.compile(finished_start_stamped_pattern)

finished_unstamped_pattern = r'(^\s*)(\[)([XS])(\] )(?!(\([1-2]\d{3}\-\d{2}\-\d{2}\)|\([1-2]\d{3}\-\d{2}\-\d{2} -> [1-2]\d{3}\-\d{2}\-\d{2}\)))'
finished_unstamped_regex = re.compile(finished_unstamped_pattern)

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

