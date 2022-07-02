import os
import pathlib
import shlex
import logging
from subprocess import Popen, PIPE

from shorthand.utils.paths import get_relative_path, is_note_path


log = logging.getLogger(__name__)


def _record_file_view(cache_directory, notes_directory, note_path,
                      history_limit=100):
    '''Record a note being viewed, so that it can be preferred in
    future search results.

    The file that stores the most recent file views stores the
        most recent view at the END of the file
    '''

    if not is_note_path(notes_directory=notes_directory, path=note_path):
        raise ValueError(f'Cannot record view for note {note_path}. '
                         f'Note does not exist')

    history_file = cache_directory + '/recent_files.txt'
    if os.path.exists(history_file):
        with open(history_file, 'r') as history_file_object:
            history_data = history_file_object.read()
    else:
        history_data = ''

    history_data = [line.strip()
                    for line in history_data.split('\n')
                    if line.strip()]

    if len(history_data) == 0:
        # There is no history yet
        history_data = [note_path]
    else:
        if note_path == history_data[-1]:
            # The viewed file is already the most recently viewed file
            return
        elif note_path in history_data:
            # The viewed file is in the history file, but
            # is not the most recently viewed file
            history_data.remove(note_path)
            history_data.append(note_path)
        else:
            # The viewed file is not in the history file
            history_data.append(note_path)
            if len(history_data) > history_limit:
                history_data = history_data[-history_limit:]

    # Make any needed parent dirs for the history file
    pathlib.Path(os.path.dirname(history_file)).mkdir(
        parents=True, exist_ok=True)

    history_string = '\n'.join(history_data) + '\n'
    with open(history_file, 'w') as history_file_object:
        history_file_object.write(history_string)


def _search_filenames(notes_directory, prefer_recent_files=True,
                      cache_directory=None, query_string=None,
                      case_sensitive=False, grep_path='grep',
                      find_path='find'):
    '''Search for a note file in the notes directory

    "prefer_recent_files" if true, will bump the most rectly
        accessed files to appear at the very top of the list
    "query_string" is a string containing one or more search
        terms. This DOES NOT support multi-word terms like the
        full-text search api does
    "case_sensitive" toggles whether the search terms should be
        matched case-sensitive
    '''

    # Early exit for no query
    if not query_string:
        return []

    find_command = '{find_path} {notes_dir} -not -path \'*/\\.*\' ' \
                   '-type f -name "*.note"'.format(
                        find_path=find_path,
                        notes_dir=notes_directory)

    log.debug(f'Running command {find_command} to find all notes files')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    find_results = [get_relative_path(notes_directory, line.strip())
                    for line in output_lines
                    if line.strip()]

    ordered_notes = find_results

    if prefer_recent_files:
        # Re-order the list of all notes based on which
        # were accessed most recently
        recent_files_path = cache_directory + '/recent_files.txt'
        if os.path.exists(recent_files_path):
            with open(recent_files_path, 'r') as recent_files_object:
                recent_files_data = recent_files_object.read()
        else:
            recent_files_data = ''
        recent_files = [file.strip()
                        for file in recent_files_data.split('\n')
                        if file.strip()]
        for recent_file in recent_files:
            if recent_file not in ordered_notes:
                continue
            else:
                ordered_notes.remove(recent_file)
                ordered_notes.append(recent_file)

    # Filter results based on query_string
    if query_string:
        if not case_sensitive:
            query_string = query_string.lower()
        query_string = query_string.replace('"', '')
        query_string = query_string.replace("'", '')
        if case_sensitive:
            search_results = [file
                              for file in ordered_notes
                              if all([query_component in file
                                      for query_component in
                                      query_string.split(' ')])
                              ]
        else:
            search_results = [file
                              for file in ordered_notes
                              if all([query_component in file.lower()
                                      for query_component in
                                      query_string.split(' ')])
                              ]
    else:
        search_results = ordered_notes

    # Bring most recently accessed matching notes to
    # the front of the list
    search_results.reverse()
    return search_results


def _search_full_text(notes_directory, query_string, case_sensitive=False,
                      aggregate_by_file=False, grep_path='grep'):
    '''Perform a full-text search through all notes and return
    matching lines with metadata

    "query_string" is a string of words which are searched for
        independently. However multi-word phrases can be searched
        for by quoting the phrase
    "case_sensitive" toggles whether or not the match is case
        sensitive
    "aggregate_by_file" determines whether all matches are aggregated per-file.
        If False, a list of dictionaries representing matches is returned
        If True, a list of dictionaries representing files with matches is
        returned. The files with the most matches appear first in the list.
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
                   '--include="*.note" --exclude-dir=\'.*\' {dir}'.format(
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

    if aggregate_by_file:

        log.debug('Aggregating search results by file')
        aggregated_results = []

        # Aggregate all matches by file
        for result in search_results:
            if result['file_path'] not in [f['file_path']
                                           for f in aggregated_results]:
                aggregated_results.append({
                    'file_path': result['file_path'],
                    'matches': [{
                        'line_number': result['line_number'],
                        'match_content': result['match_content']
                    }]
                })
            else:
                for entry in aggregated_results:
                    if entry['file_path'] == result['file_path']:
                        entry['matches'].append({
                            'line_number': result['line_number'],
                            'match_content': result['match_content']
                        })
                        break

        # Sort files by number of matches
        aggregated_results.sort(key=lambda result: len(result['matches']),
                                reverse=True)
        search_results = aggregated_results

    return {
        "items": search_results,
        "count": len(search_results)
    }
