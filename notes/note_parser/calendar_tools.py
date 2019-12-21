import json
import re
from datetime import datetime
from subprocess import Popen, PIPE
import shlex

from note_parser.utils.patterns import DATED_HEADING_PATTERN, escape_for_grep


dated_heading_regex = re.compile(DATED_HEADING_PATTERN)


def get_calendar(notes_directory, directory_filter=None):

    events = []
    calendar = {}

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = 'grep -rn "{pattern}" {dir} | grep -v "\\.git"'.format(
            pattern=escape_for_grep(DATED_HEADING_PATTERN),
            dir=search_directory)

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    # Create events from parsed headings
    for line in output_lines:

        if not line.strip():
            continue

        split_line = line.split(':', 2)
        file_path = split_line[0]
        line_number = split_line[1]
        heading_raw = split_line[2]

        heading_match = dated_heading_regex.match(heading_raw)
        if not heading_match:
            print('NO MATCH FOUND?!?!')
        else:
            heading_text = heading_match.group(3).strip()
            date = heading_match.group(4).strip()

        if notes_directory in file_path:
            file_path = file_path[len(notes_directory):]

        parsed_heading = {
            "file_path": file_path,
            "line_number": line_number,
            "event": heading_text,
            "date": date
        }

        events.append(parsed_heading)

    # Create Calendar from events
    for event in events:
        event_date = event['date']

        event_year = event_date[:4]
        event_month = event_date[5:7]
        event_day = event_date[8:]

        calendar.setdefault(event_year, {})
        calendar[event_year].setdefault(event_month, {})
        calendar[event_year][event_month].setdefault(event_day, [])
        calendar[event_year][event_month][event_day].append(event)

    return calendar
