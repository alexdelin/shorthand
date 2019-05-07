import re
from datetime import datetime
from subprocess import Popen, PIPE
import shlex

from note_parser.utils.patterns import TAG_PATTERN


tag_regex = re.compile(TAG_PATTERN)


def get_tags(notes_directory, directory_filter=None):

    tag_items = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = 'grep -r "{pattern}" {dir} | grep -v "\\.git"'.format(
            pattern=TAG_PATTERN,
            dir=search_directory)
    print(grep_command)

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.split('\n')

    print(output_lines)
    for line in output_lines:

        if not line.strip():
            continue

        tags = tag_regex.findall(line)
        tag_items.extend(tags)

    # Only keep a unique set of tags with no wrapping colons
    tag_items = [item.strip(':') for item in list(set(tag_items))]
    # Only keep tags with at least one letter
    tag_items = [item for item in tag_items if any(char.isalpha() for char in item)]
    return tag_items
