import difflib
import logging
from datetime import UTC, datetime
import os
from subprocess import PIPE, Popen
from typing import List, Optional

from shorthand.notes import _is_note_path, _get_note
from shorthand.history.types import NoteDiff, NoteDiffInfo, NoteDiffTimestamp, NoteDiffType, HISTORY_PATH
from shorthand.types import DirectoryPath, ExecutablePath, NotePath, RawNoteContent
from shorthand.utils.paths import get_relative_path


log = logging.getLogger(__name__)


def get_unified_diff(old: RawNoteContent, new: RawNoteContent,
                     path: NotePath, author: str = 'Unknown'
                     ) -> NoteDiff:
    timestamp = datetime.now(UTC).isoformat(timespec='milliseconds')
    header_lines = [
        f'Author: {author}\n',
        f'Time: {timestamp}\n',
        f'\n',
        f'diff --git a{path} b{path}\n'
    ]

    if old == new:
        return get_empty_edit_diff(path, author)

    diff_lines = list(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f'{path} (old)',
        tofile=f'{path} (new)',
        lineterm='\n'))
    cleaned_diff_lines = []
    for line in diff_lines:
        if line.endswith('\n'):
            cleaned_diff_lines.append(line)
        else:
            cleaned_diff_lines.append(line + '\n')

    log.debug(f'Got calculated diff {cleaned_diff_lines}')
    unified_diff = ''.join(header_lines + cleaned_diff_lines)
    log.debug(f'Got unified diff {unified_diff}')

    return unified_diff


def calculate_diff_for_edit(notes_directory: DirectoryPath,
                            note_path: NotePath,
                            new_content: RawNoteContent) -> Optional[NoteDiff]:
    old_content = _get_note(notes_directory, note_path)
    if old_content == new_content:
        return None
    return get_unified_diff(old_content, new_content, note_path)


def calculate_diff_for_move(old_note_path: NotePath,
                            new_note_path: NotePath,
                            author: str = 'Unknown') -> NoteDiff:
    # Can only be applied with GNU Patch
    timestamp = datetime.now(UTC).isoformat(timespec='milliseconds')
    return \
f'''Author: {author}
Time: {timestamp}

diff --git a{old_note_path} b{new_note_path}
similarity index 100%
rename from {old_note_path}
rename to {new_note_path}'''


def calculate_diff_for_create(note_path: NotePath,
                              author: str = 'Unknown') -> NoteDiff:
    # Only works with GNU Patch
    timestamp = datetime.now(UTC).isoformat(timespec='milliseconds')
    return \
f'''Author: {author}
Time: {timestamp}

diff --git a{note_path} b{note_path}
new file mode 100644'''


def calculate_diff_for_delete(notes_directory: DirectoryPath,
                              note_path: NotePath,
                              author: str = 'Unknown') -> NoteDiff:
    # Only works with GNU Patch
    timestamp = datetime.now(UTC).isoformat(timespec='milliseconds')
    old_content = _get_note(notes_directory, note_path)
    diff_lines = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        [],
        fromfile=note_path, tofile=note_path)
    diff = ''.join(diff_lines)

    return \
f'''Author: {author}
Time: {timestamp}

diff --git a{note_path} b{note_path}
deleted file mode 100644
{diff}'''


def get_empty_edit_diff(note_path: NotePath,
                        author: str = 'Unknown') -> NoteDiff:
    '''A diff which represents no changes being made to a note.
       Used in the case where multiple edits are merged together which
       cancel out and results in no net-changes being made to the note
    '''
    timestamp = datetime.now(UTC).isoformat(timespec='milliseconds')
    return \
f'''Author: {author}
Time: {timestamp}

diff --git a{note_path} b{note_path}
no changes made'''


def save_diff(notes_directory: DirectoryPath, note_path: NotePath,
              diff: NoteDiff, timestamp: datetime, diff_type: NoteDiffType) -> None:

    utc_time_string = timestamp.isoformat(timespec='milliseconds')
    diff_path = f'{notes_directory}/' + \
                f'{HISTORY_PATH}' + \
                f'{note_path}/diffs/' + \
                f'{timestamp.year}/' + \
                f'{timestamp.month}/' + \
                f'{timestamp.day}/' + \
                f'{utc_time_string}.{diff_type}.diff'

    if os.path.exists(diff_path):
        raise ValueError(f'A diff already exists at path {diff_path}')

    daily_diffs_dir = os.path.dirname(diff_path)
    if not os.path.exists(daily_diffs_dir):
        os.makedirs(daily_diffs_dir)

    with open(diff_path, 'w') as f:
        f.write(diff)


def delete_diff(notes_directory: DirectoryPath, note_path: NotePath,
                timestamp: NoteDiffTimestamp, diff_type: NoteDiffType) -> None:
    parsed_diff_time = datetime.fromisoformat(timestamp)

    diff_path = f'{notes_directory}/' + \
                f'{HISTORY_PATH}' + \
                f'{note_path}/diffs/' + \
                f'{parsed_diff_time.year}/' + \
                f'{parsed_diff_time.month}/' + \
                f'{parsed_diff_time.day}/' + \
                f'{timestamp}.{diff_type}.diff'

    if not os.path.exists(diff_path):
        raise ValueError(f'Diff not found for note {note_path} action {diff_type} and time {timestamp}')

    os.remove(diff_path)


def extract_paths_from_move_diff(diff: NoteDiff):
    diff_lines = diff.splitlines()
    from_path = None
    to_path = None
    for line in diff_lines:
        if line.startswith('rename from'):
            from_path = line.split(' from ', 1)[1]
        if line.startswith('rename to'):
            to_path = line.split(' to ', 1)[1]

    return {
        'from': from_path,
        'to': to_path
    }


def _list_diffs_for_note(notes_directory: DirectoryPath,
                         note_path: NotePath,
                         find_path: ExecutablePath = 'find'
                         ) -> List[NoteDiffInfo]:
    if not _is_note_path(notes_directory, note_path, must_exist=False):
        raise ValueError(f'The path {note_path} is not a valid note path')

    find_command = f'{find_path} {notes_directory}/' + \
                   f'{HISTORY_PATH}{note_path} ' + \
                   f'-type f -name "*.diff"'

    log.debug(f'Running command {find_command} to list note diffs')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    diff_files = [get_relative_path(notes_directory, line.strip())
                  for line in output_lines
                  if line.strip()]

    response = []
    for diff_file in diff_files:
        filename = diff_file.split('/')[-1]
        diff_type = filename.split('.')[-2]
        timestamp = filename.rsplit('.', 2)[0]
        if diff_type == 'move':
            full_diff = _get_note_diff(notes_directory, note_path, timestamp, diff_type)
            move_diff_paths = extract_paths_from_move_diff(full_diff)
            if move_diff_paths['from'] == note_path:
                move_direction = 'out'
            else:
                move_direction = 'in'
            response.append({
                'diff_type': diff_type,
                'timestamp': timestamp,
                'from_path': move_diff_paths['from'],
                'to_path': move_diff_paths['to'],
                'move_direction': move_direction
            })
        else:
            response.append({
                'diff_type': diff_type,
                'timestamp': timestamp
            })

    response.sort(key=lambda x: x['timestamp'], reverse=True)

    return response


def _get_note_diff(notes_directory: DirectoryPath,
                   note_path: NotePath,
                   timestamp: NoteDiffTimestamp,
                   diff_type: NoteDiffType) -> NoteDiff:
    if not _is_note_path(notes_directory, note_path, must_exist=False):
        raise ValueError(f'The path {note_path} is not a valid note path')

    parsed_diff_time = datetime.fromisoformat(timestamp)

    diff_path = f'{notes_directory}/' + \
            f'{HISTORY_PATH}' + \
            f'{note_path}/diffs/' + \
            f'{parsed_diff_time.year}/' + \
            f'{parsed_diff_time.month}/' + \
            f'{parsed_diff_time.day}/' + \
            f'{timestamp}.{diff_type}.diff'

    if not os.path.exists(diff_path):
        raise ValueError(f'Diff not found for note {note_path} and timestamp {timestamp}')

    with open(diff_path, 'r') as f:
        return f.read()
