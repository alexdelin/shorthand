'''
These utilities allow for tracking the full edit history of a given note
over time.
This introduces two new types of supporting resources which are used to
construct the modification history of a note. These are:
1. Daily Starting Versions - The version of a note on top of which all
   modifications in a given day (UTC Time) were made
2. Diffs - Incremental changes made to a file every time it is updated.
   Supported types of operations are:
     - Arbitrary content changes
     - File Renames
     - File Creation
     - File Deletion
'''
import os
import shutil
import difflib
import logging
import tempfile
from datetime import date, datetime, UTC, timedelta
from subprocess import PIPE, Popen
from typing import List, Literal, Optional, Required, TypedDict

from shorthand.notes import _get_note, _is_note_path
from shorthand.types import DirectoryPath, ExecutablePath, NotePath, RawNoteContent, Subdir
from shorthand.utils.paths import get_full_path, get_relative_path


HISTORY_PATH = '.shorthand/history'

MERGE_CUTOFF_LIMIT_MIN = 15


log = logging.getLogger(__name__)


type NoteDiff = str
'''A git-formatted diff representing a modification made to a note'''

type NoteDiffTimestamp = str
'''An ISO-8601 timestamp for the UTC time that a note was modified
   with millisecond-precision. Includes the `+00:00` UTC timezone offset'''

type NoteDiffType = Literal['create', 'edit', 'move', 'delete']
'''Options for types of changes which can be recorded as diffs'''

class NoteDiffInfo(TypedDict, total=False):
    diff_type: Required[NoteDiffType]
    timestamp: Required[NoteDiffTimestamp]
    from_path: NotePath
    to_path: NotePath
    move_direction: Literal['in', 'out']

type NoteVersion = str
'''The raw note content of a historical version of a note,
   as of the start of a given UTC day'''

type NoteVersionTimestamp = str
'''An ISO-8601 time stamp for the UTC time that a version was created
   with millisecond-precision. Includes the `+00:00` UTC timezone offset

   By default, this is the timestamp of the start of day UTC time'''


def ensure_note_version(notes_directory: DirectoryPath,
                        note_path: NotePath,
                        timestamp: datetime,
                        find_path: ExecutablePath = 'find') -> None:
    '''Ensure that a daily starting version exists for the specified note and
       the current UTC day

       A note must currently exist at the specified note path

       `use_exact_time` is used in the case of moves, if there is already
       a version present for the note for the beginning of the day
    '''

    if not _is_note_path(notes_directory, note_path):
        raise ValueError(f'No note found at path {note_path}')

    utc_date = timestamp.date()

    if note_version_exists_for_date(notes_directory, note_path,
                                    utc_date, find_path):
        return

    timestamp_string = timestamp.isoformat(timespec='milliseconds')
    note_version_path = f'{notes_directory}/' + \
                        f'{HISTORY_PATH}' + \
                        f'{note_path}/{timestamp_string}.version'

    note_history_dir = os.path.dirname(note_version_path)
    if not os.path.exists(note_history_dir):
        os.makedirs(note_history_dir)

    full_note_path = get_full_path(notes_directory, note_path)
    shutil.copy2(full_note_path, note_version_path)


def note_version_exists_for_date(notes_directory: DirectoryPath,
                                 note_path: NotePath,
                                 utc_date: date,
                                 find_path: ExecutablePath = 'find') -> bool:

    date_string = utc_date.isoformat()
    find_command = f'{find_path} {notes_directory}/{HISTORY_PATH}{note_path} ' + \
                   f'-type f -name "{date_string}*.version"'

    log.debug(f'Running command {find_command} to list note versions')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    version_files = [get_relative_path(notes_directory, line.strip())
                     for line in output_lines
                     if line.strip()]

    if len(version_files):
        return True

    return False


def add_note_version_for_move(notes_directory: DirectoryPath,
                              source: NotePath,
                              destination: NotePath,
                              timestamp: datetime) -> None:
    '''Add a note version with the precise current UTC timestamp
       this should only be called if a version file for the destination
       note already exists for the beginning of the current day
    '''

    # Increment the version timestamp by 1 millisecond so that it shows
    # up after the move diffs in the edit timeline
    timestamp = timestamp + timedelta(milliseconds=1)
    timestamp_string = timestamp.isoformat(timespec='milliseconds')
    note_version_path = f'{notes_directory}/' + \
                        f'{HISTORY_PATH}' + \
                        f'{destination}/{timestamp_string}.version'

    if os.path.exists(note_version_path):
        raise ValueError(f'Note version already exists at path {note_version_path}')

    note_history_dir = os.path.dirname(note_version_path)
    if not os.path.exists(note_history_dir):
        os.makedirs(note_history_dir)

    full_note_path = get_full_path(notes_directory, source)
    shutil.copy2(full_note_path, note_version_path)


def _list_note_versions(notes_directory: DirectoryPath,
                        note_path: NotePath,
                        find_path: ExecutablePath = 'find'
                        ) -> List[NoteVersionTimestamp]:
    '''List historical versions which are stored for a specified note

       The specified note does not currently need to exist, it could
       have already been deleted or moved
    '''

    if not _is_note_path(notes_directory, note_path, must_exist=False):
        raise ValueError(f'The path {note_path} is not a valid note')

    find_command = f'{find_path} {notes_directory}/{HISTORY_PATH}{note_path} ' + \
                   '-type f -name "*.version"'

    log.debug(f'Running command {find_command} to list note versions')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    version_files = [get_relative_path(notes_directory, line.strip())
                     for line in output_lines
                     if line.strip()]

    return [f.split('/')[-1][:-8] for f in version_files]


def _get_note_version(notes_directory: DirectoryPath,
                      note_path: NotePath,
                      version_timestamp: NoteVersionTimestamp) -> NoteVersion:
    '''Get a specified historical version of a give note

       The specified note does not currently need to exist, it could
       have already been deleted or moved
    '''

    if not _is_note_path(notes_directory, note_path, must_exist=False):
        raise ValueError(f'The path {note_path} is not a valid note')

    note_version_path = f'{notes_directory}/' + \
                        f'{HISTORY_PATH}' + \
                        f'{note_path}/{version_timestamp}.version'

    if not os.path.exists(note_version_path):
        raise ValueError(f'A Version for note {note_path} on date ' + \
                         f'{version_timestamp} does not exist')

    with open(note_version_path, 'r') as f:
        return f.read()


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


def apply_diffs(starting_content: RawNoteContent,
                diffs: List[NoteDiff],
                patch_path: ExecutablePath = 'patch',
                reverse: bool = False) -> RawNoteContent:
    '''Apply one or more patches to a file with GNU patch

       Patches are applied in the order they are provided

       If `reverse` is set, then patches are undone from the starting content
    '''

    # Remove empty patches from being applied,
    # because it will cause patch to return an error code
    filtered_diffs = [d for d in diffs if '---' in d]
    if not filtered_diffs:
        return starting_content

    with tempfile.TemporaryDirectory() as tmpdir:
        original_filename = f'{tmpdir}/original.txt'
        patched_filename = f'{tmpdir}/patched.txt'
        diff_filenames = []

        with open(original_filename, 'w') as f:
            f.write(starting_content)
            if not starting_content.endswith('\n'):
                f.write('\n')

        for idx, diff_content in enumerate(filtered_diffs):
            diff_filename = f'{tmpdir}/diff_{idx}.txt'
            with open(diff_filename, 'w') as f:
                f.write(diff_content)
                if not starting_content.endswith('\n'):
                    f.write('\n')
            diff_filenames.append(diff_filename)

        patch_command = f'{patch_path} {original_filename}'
        if reverse:
            patch_command += ' -R'
        for diff in diff_filenames:
            patch_command += f' -i {diff}'
        patch_command += f' -o {patched_filename}'

        log.warning(f'Running command {patch_command} to apply diffs')
        proc = Popen(patch_command, stdout=PIPE, stderr=PIPE, shell=True)
        output, err = proc.communicate()
        status_code = proc.returncode

        if status_code > 1:
            raise ValueError(f'Error while calculating diff {output.decode()} {err.decode()}')

        with open(patched_filename, 'r') as f:
            return f.read()


def _store_history_for_note_edit(notes_directory: DirectoryPath,
                                 note_path: NotePath,
                                 new_content: RawNoteContent,
                                 find_path: ExecutablePath = 'find',
                                 patch_path: ExecutablePath = 'patch') -> None:
    timestamp = datetime.now(UTC)

    ensure_note_version(notes_directory, note_path, timestamp)

    # If the latest diff is an edit diff
    #   which was made within the last 5 minutes
    #   then merge this change into the latest diff
    all_diffs = _list_diffs_for_note(notes_directory, note_path, find_path)
    if all_diffs:
        latest_diff = all_diffs[0]
        merge_cutoff_time = timestamp - timedelta(minutes=MERGE_CUTOFF_LIMIT_MIN)
        merge_cutoff_time = merge_cutoff_time.isoformat(timespec='milliseconds')
        if latest_diff and latest_diff['diff_type'] == 'edit' \
                       and latest_diff['timestamp'] > merge_cutoff_time:
            # We are merging these changes into the latest diff
            current_version = _get_note(notes_directory, note_path)
            latest_diff_content = _get_note_diff(notes_directory, note_path, latest_diff['timestamp'], latest_diff['diff_type'])
            pre_edit_state = apply_diffs(current_version, [latest_diff_content], patch_path, reverse=True)
            combined_diff = get_unified_diff(pre_edit_state, new_content, note_path)
            save_diff(notes_directory, note_path, combined_diff, timestamp, 'edit')
            delete_diff(notes_directory, note_path, latest_diff['timestamp'], latest_diff['diff_type'])
            return None

    # If we are not doing a merge
    diff = calculate_diff_for_edit(notes_directory, note_path, new_content)
    if diff:
        save_diff(notes_directory, note_path, diff, timestamp, 'edit')


def _store_history_for_note_move(notes_directory: DirectoryPath,
                                 old_note_path: NotePath,
                                 new_note_path: NotePath,
                                 find_path: ExecutablePath = 'find'
                                 ) -> None:
    '''Ensure that all needed edit history is created for a note being moved

       If `validate_history_clashes` is set, then a check will be done that
       the new note path does not already have history associated with it for
       the current day. This eliminates edge cases where history can be
       displayed incorrectly
    '''

    if not _is_note_path(notes_directory, old_note_path) and not \
           _is_note_path(notes_directory, new_note_path, must_exist=False):
        raise ValueError(f'Cannot track move history. Neither {old_note_path} ' + \
                         f'or {new_note_path} are valid note paths')

    timestamp = datetime.now(UTC)
    if _is_note_path(notes_directory, new_note_path, must_exist=False) and \
            note_version_exists_for_date(
                notes_directory=notes_directory, note_path=new_note_path,
                utc_date=timestamp.date(), find_path=find_path):
        # If a version already exists for today at the path that we are
        # moving the note to, add another version file with the exact current
        # timestamp. This new version will be used as the base version for any
        # edits made after this point in time
        #
        # This is dangerous because the version file will reflect the move
        # before the file in the notes directory has actually been moved
        add_note_version_for_move(notes_directory, old_note_path,
                                  new_note_path, timestamp)
        # return

    diff = calculate_diff_for_move(old_note_path, new_note_path)
    if _is_note_path(notes_directory, old_note_path):
        ensure_note_version(notes_directory, old_note_path, timestamp)
        save_diff(notes_directory, old_note_path, diff, timestamp, 'move')
    if _is_note_path(notes_directory, new_note_path, must_exist=False):
        save_diff(notes_directory, new_note_path, diff, timestamp, 'move')


def _store_history_for_directory_move(notes_directory: DirectoryPath,
                                      old_directory_path: Subdir,
                                      new_directory_path: Subdir,
                                      find_path: ExecutablePath = 'find'
                                      ) -> None:
    '''
    '''
    old_full_dir_path = get_full_path(notes_directory, old_directory_path)
    new_full_dir_path = get_full_path(notes_directory, new_directory_path)

    if os.path.exists(new_full_dir_path):
        raise ValueError(f'Target directory {new_directory_path} already exists')

    # Ensure that version history exists for every note being moved
    find_command = f'{find_path} {old_full_dir_path} ' + \
                   '-type f -name "*.note"'

    log.debug(f'Running command {find_command} to list notes')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().splitlines()

    note_paths = [get_relative_path(notes_directory, line.strip())
                  for line in output_lines
                  if line.strip()]

    for note_path in note_paths:
        new_note_path = note_path.replace(
            f'{old_directory_path}',
            f'{new_directory_path}')
        _store_history_for_note_move(
            notes_directory=notes_directory,
            old_note_path=note_path,
            new_note_path=new_note_path,
            find_path=find_path)


def _store_history_for_note_create(notes_directory: DirectoryPath,
                                   note_path: NotePath) -> None:

    timestamp = datetime.now(UTC)

    if not _is_note_path(notes_directory, note_path, must_exist=False):
        raise ValueError(f'The path {note_path} is not a valid note path')

    diff = calculate_diff_for_create(note_path)
    save_diff(notes_directory, note_path, diff, timestamp, 'create')


def _store_history_for_note_delete(notes_directory: DirectoryPath,
                                   note_path: NotePath) -> None:
    timestamp = datetime.now(UTC)
    ensure_note_version(notes_directory, note_path, timestamp)
    diff = calculate_diff_for_delete(notes_directory, note_path)
    save_diff(notes_directory, note_path, diff, timestamp, 'delete')


def _store_history_for_directory_delete(notes_directory: DirectoryPath,
                                        directory_path: Subdir,
                                        find_path: ExecutablePath = 'find'
                                        ) -> None:
    full_dir_path = get_full_path(notes_directory, directory_path)
    if not os.path.exists(full_dir_path):
        raise ValueError(f'Directory {directory_path} to delete does not exist')

    # Ensure that version history exists for every note being moved
    find_command = f'{find_path} {full_dir_path} ' + \
                   '-type f -name "*.note"'

    log.debug(f'Running command {find_command} to list notes')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().splitlines()

    note_paths = [get_relative_path(notes_directory, line.strip())
                  for line in output_lines
                  if line.strip()]

    for note_path in note_paths:
        _store_history_for_note_delete(
            notes_directory=notes_directory,
            note_path=note_path)
