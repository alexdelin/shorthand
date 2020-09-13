import shlex
import logging
from subprocess import Popen, PIPE

from shorthand.utils.paths import get_full_path, get_relative_path


log = logging.getLogger(__name__)


def record_file_view(cache_directory, relative_path, history_limit=100):
    '''Record a note being viewed, so that it can be preferred in
    future search results.
    '''

    history_file = cache_directory + '/recent_files.txt'
    with open(history_file, 'r') as history_file_object:
        history_data = history_file_object.read()

    history_data = [line.strip()
                    for line in history_data.split('\n')
                    if line.strip()]

    if len(history_data) == 0:
        # There is no history yet
        history_data = [relative_path]
    else:
        if relative_path == history_data[0]:
            # The viewed file is already the most recently viewed file
            return
        elif relative_path in history_data:
            # The viewed file is in the history file, but
            # is not the most recently viewed file
            history_data.remove(relative_path)
            history_data.insert(0, relative_path)
        else:
            # The viewed file is not in the history file
            history_data.insert(0, relative_path)
            if len(history_data) > history_limit:
                history_data = history_data[-history_limit:]

    history_string = '\n'.join(history_data) + '\n'
    with open(history_file, 'w') as history_file_object:
        history_file_object.write(history_string)


def filename_search(notes_directory, prefer_recent_files=True,
                    cache_directory=None, query_string=None,
                    case_sensitive=False, grep_path='grep'):
    '''Search for a note file in the notes directory

    "prefer_recent_files" if true, will bump the most rectly
        accessed files to appear at the very top of the list
    "query_string" is a string containing one or more search
        terms. This DOES NOT support multi-word terms like the
        full-text search api does
    "case_sensitive" toggles whether the search terms should be
        matched case-sensitive
    '''

    if prefer_recent_files:
        recent_files_path = cache_directory + '/recent_files.txt '
    else:
        recent_files_path = ''

    find_command = 'gfind {notes_dir} -name "*.note" -printf "/%P\\n" | '\
                   'cat {recent_files}- | cat -n - | '\
                   'sort -uk2 | sort -nk1 | cut -f2-'.format(
                        notes_dir=notes_directory,
                        recent_files=recent_files_path)

    grep_filter_mode = ''
    if not case_sensitive:
        grep_filter_mode += ' -i'

    if query_string:
        query_string = query_string.replace('"', '')
        query_string = query_string.replace("'", '')
        query_components = query_string.strip().split(' ')
        for component in query_components:
            new_filter = ' | {grep_path}{mode} "{pattern}"'.format(
                            grep_path=grep_path,
                            mode=grep_filter_mode,
                            pattern=component)
            find_command = find_command + new_filter
    log.debug(f'Running command {find_command} to find notes files')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    results = [get_relative_path(notes_directory, line.strip())
               for line in output_lines
               if line.strip()]
    return results


def search_notes(notes_directory, query_string, type=None,
                 case_sensitive=False, grep_path='grep'):
    '''Perform a full-text search through all notes and return
    matching lines with metadata

    "query_string" is a string of words which are searched for
        independently. However multi-word phrases can be searched
        for by quoting the phrase
    "type" is the type of objects to search (todos, questions, etc.)
    "case_sensitive" toggles whether or not the match is case
        sensitive
    '''

    query_components = shlex.split(query_string)

    # Early exit for empty query
    if not query_components:
        return []

    # Add safe handling of quoted phrases
    safe_components = []
    for component in query_components:
        if component[0] == '"' and component[-1] == '"':
            safe_components.append(component[1:-1])
        else:
            safe_components.append(component)

    grep_mode = '-rn'
    grep_filter_mode = ''
    if not case_sensitive:
        grep_mode += 'i'
        grep_filter_mode += ' -i'

    grep_command = '{grep_path} {mode} "{pattern}" '\
                   '--include="*.note" {dir}'.format(
                        grep_path=grep_path,
                        mode=grep_mode,
                        pattern=query_components[0],
                        dir=notes_directory)

    for additional_filter in query_components[1:]:
        new_filter = ' | {grep_path}{mode} "{pattern}"'.format(
                        grep_path=grep_path,
                        mode=grep_filter_mode,
                        pattern=additional_filter)
        grep_command = grep_command + new_filter

    log.debug(f'Running command {grep_command} to get search results')

    proc = Popen(
        grep_command,
        stdout=PIPE, stderr=PIPE,
        shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    search_results = []

    for line in output_lines:

        if not line.strip():
            continue

        split_line = line.split(':', 2)
        file_path = split_line[0].strip()
        line_number = split_line[1].strip()
        match_content = split_line[2].strip()

        # Return all paths as relative paths within the notes dir
        if notes_directory in file_path:
            file_path = file_path[len(notes_directory):]

        processed_line = {
            'file_path': file_path,
            'line_number': line_number,
            'match_content': match_content,
        }

        search_results.append(processed_line)

    return {
        "items": search_results,
        "count": len(search_results)
    }


def get_note(notes_directory, path):
    '''Get the full raw content of a note as a string
    given its path, which can be either a relative path
    within the notes directory or a full path on the
    filesystem
    '''

    full_path = get_full_path(notes_directory, path)

    with open(full_path, 'r') as note_file_object:
        note_content = note_file_object.read()

    return note_content
