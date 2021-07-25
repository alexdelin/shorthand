import re
from subprocess import Popen, PIPE
import logging

from shorthand.utils.patterns import TAG_PATTERN, TAG_FILTER


tag_regex = re.compile(TAG_PATTERN)


log = logging.getLogger(__name__)


def _get_tags(notes_directory, directory_filter=None, grep_path='grep'):

    tag_items = []

    search_directory = notes_directory
    if directory_filter:
        if search_directory[-1] != '/':
            search_directory += '/'
        search_directory += directory_filter

    grep_command = '{grep_path} -Pr "{pattern}" '\
                   '--include="*.note" {dir}'.format(
                        grep_path=grep_path,
                        pattern=TAG_FILTER,
                        dir=search_directory)
    log.debug(f'Running grep command {grep_command} to get tags')

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    for line in output_lines:

        if not line.strip():
            continue

        tags = tag_regex.findall(line)
        # Matches are returned as tuples because the pattern
        # has two groups. We only want to keep the first one
        tags = [tag[0] for tag in tags]
        tag_items.extend(tags)

    # Only keep a unique set of tags with no wrapping colons
    log.debug(tag_items)
    tag_items = [item.strip().strip(':') for item in list(set(tag_items))]
    # Only keep tags with at least one letter
    tag_items = [item
                 for item in tag_items
                 if any(char.isalpha() for char in item)]
    tag_items.sort()
    return tag_items


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
