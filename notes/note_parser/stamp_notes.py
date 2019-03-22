import re
from datetime import datetime
from subprocess import Popen, PIPE
from note_parser.utils.patterns import CATCH_ALL_PATTERN, \
        VALID_INCOMPLETE_PATTERN, VALID_COMPLETE_PATTERN, \
        UNFINISHED_UNSTAMPED_PATTERN, FINISHED_START_STAMPED_PATTERN, \
        FINISHED_UNSTAMPED_PATTERN


proc = Popen(
    'grep -r {pattern} . | grep -v {filter_1} | grep -v {filter_2}'.format(
        pattern=CATCH_ALL_PATTERN,
        filter_1=VALID_INCOMPLETE_PATTERN,
        filter_2=VALID_COMPLETE_PATTERN),
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

