import re
from datetime import datetime
from subprocess import Popen, PIPE
import shlex
import logging

from shorthand.utils.paths import get_relative_path, get_display_path
from shorthand.utils.patterns import GPS_PATTERN


gps_regex = re.compile(GPS_PATTERN)


log = logging.getLogger(__name__)


def get_locations(notes_directory, directory_filter=None, grep_path='grep'):

    location_items = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = '{grep_path} -Prn "{pattern}" {dir} | {grep_path} -v "\\.git"'.format(
            grep_path=grep_path,
            pattern=GPS_PATTERN,
            dir=search_directory)
    log.debug(f'Running grep command {grep_command} to get locations')

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
        file_path = split_line[0].strip()
        line_number = split_line[1].strip()
        match_content = split_line[2].strip()

        locations = gps_regex.findall(match_content)

        # Clean up file path and create display path
        file_path = get_relative_path(notes_directory, file_path)
        display_path = get_display_path(file_path, directory_filter)

        for match in locations:
            log.debug('Got Match')
            log.debug(match)
            extracted_location = {
                "latitude": match[1],
                "longitude": match[3],
                "name": match[5],
                'file_path': file_path,
                'display_path': display_path,
                'line_number': line_number,
            }
            # locations = [location[0] for location in locations]
            location_items.append(extracted_location)

    # Only keep a unique set of tags with no wrapping colons
    log.debug(location_items)

    return location_items


def extract_tags(text):

    tags = []

    if ':' not in text:
        return tags, text
    else:
        raw_tags = tag_regex.findall(text)
        raw_tags = [tag[0] for tag in raw_tags]
        # Only keep a unique set of tags with no wrapping colons
        tags = [item.strip().strip(':') for item in list(set(raw_tags))]
        # Only keep tags with at least one letter
        tags = [item for item in tags if any(char.isalpha() for char in item)]
        tags.sort()
        clean_text = re.sub(tag_regex, '', text).strip()
        return tags, clean_text
