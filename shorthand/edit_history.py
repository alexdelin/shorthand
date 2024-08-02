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
from datetime import datetime, UTC
from subprocess import PIPE, Popen
from typing import List

from shorthand.notes import _get_note
from shorthand.types import DirectoryPath, ExecutablePath, NotePath, RawNoteContent
from shorthand.utils.paths import get_full_path, get_relative_path


HISTORY_PATH = '.shorthand/history'


log = logging.getLogger(__name__)


type NoteDiff = str
'''A git-formatted diff representing a modification made to a note'''

type NoteDiffTimestamp = str
'''An ISO-8601 timestamp for the UTC time that a note was modified'''

type NoteVersion = str
'''The raw note content of a historical version of a note,
   as of the start of a given UTC day'''

type NoteVersionDate = str
'''An ISO-8601 date stamp for the UTC date of a note version'''


def ensure_daily_starting_version(notes_directory: DirectoryPath,
                                  note_path: NotePath) -> None:
    current_utc_date = datetime.now(UTC).date().isoformat()
    daily_starting_version_path = f'{notes_directory}/' + \
                                  f'{HISTORY_PATH}' + \
                                  f'{note_path}/{current_utc_date}.version'

    if os.path.exists(daily_starting_version_path):
        return

    note_history_dir = os.path.dirname(daily_starting_version_path)
    if not os.path.exists(note_history_dir):
        os.makedirs(note_history_dir)

    full_note_path = get_full_path(notes_directory, note_path)
    if not os.path.exists(full_note_path):
        raise ValueError(f'Note at path {note_path} does not exist')
    shutil.copy2(full_note_path, daily_starting_version_path)


def _list_versions_for_note(notes_directory: DirectoryPath,
                            note_path: NotePath,
                            find_path: ExecutablePath = 'find'
                            ) -> List[NoteVersionDate]:
    find_command = f'{find_path} {notes_directory}/{HISTORY_PATH}{note_path} ' + \
                   '-type f -name "*.version"'

    log.debug(f'Running command {find_command} to list note versions')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    version_files = [get_relative_path(notes_directory, line.strip())
                     for line in output_lines
                     if line.strip()]

    return [f.split('/')[-1].split('.')[0] for f in version_files]


def _get_note_version(notes_directory: DirectoryPath,
                      note_path: NotePath,
                      version_date: NoteVersionDate) -> NoteVersion:
    return ''


def calculate_diff_for_edit(notes_directory: DirectoryPath,
                            note_path: NotePath,
                            new_content: RawNoteContent) -> NoteDiff:
    old_content = _get_note(notes_directory, note_path)
    diff_lines = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=note_path, tofile=note_path)
    return ''.join(diff_lines)


def calculate_diff_for_move(old_note_path: NotePath,
                            new_note_path: NotePath) -> NoteDiff:
    # Only works with GNU Patch
    return f'''
    diff --git a/{old_note_path} b/{new_note_path}
    similarity index 100%
    rename from {old_note_path}
    rename to {new_note_path}'''


def calculate_diff_for_create(note_path: NotePath) -> NoteDiff:
    # Only works with GNU Patch
    return f'''
    diff --git a/{note_path} b/{note_path}
    new file mode 100644'''


def calculate_diff_for_delete(notes_directory: DirectoryPath,
                              note_path: NotePath) -> NoteDiff:
    # Only works with GNU Patch
    old_content = _get_note(notes_directory, note_path)
    diff_lines = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        [],
        fromfile=note_path, tofile=note_path)
    diff = ''.join(diff_lines)
    return f'''
    diff --git a/{note_path} b/{note_path}
    deleted file mode 100644
    {diff}'''


def save_diff(notes_directory: DirectoryPath, note_path: NotePath,
              diff: NoteDiff) -> None:
    current_utc_time = datetime.now(UTC)
    current_utc_time_string = current_utc_time.isoformat(timespec='milliseconds')
    diff_path = f'{notes_directory}/' + \
                f'{HISTORY_PATH}' + \
                f'{note_path}/diffs/' + \
                f'{current_utc_time.year}/' + \
                f'{current_utc_time.month}/' + \
                f'{current_utc_time.day}/' + \
                f'{current_utc_time_string}.diff'

    if os.path.exists(diff_path):
        raise ValueError(f'A diff already exists at path {diff_path}')

    daily_diffs_dir = os.path.dirname(diff_path)
    if not os.path.exists(daily_diffs_dir):
        os.makedirs(daily_diffs_dir)

    with open(diff_path, 'w') as f:
        f.write(diff)


def _store_history_for_note_edit(notes_directory: DirectoryPath,
                                 note_path: NotePath,
                                 new_content: RawNoteContent
                                 ) -> None:
    ensure_daily_starting_version(notes_directory, note_path)
    diff = calculate_diff_for_edit(notes_directory, note_path, new_content)
    save_diff(notes_directory, note_path, diff)


def _store_history_for_note_move(notes_directory: DirectoryPath,
                                 old_note_path: NotePath,
                                 new_note_path: NotePath) -> None:
    pass


def _store_history_for_note_create(notes_directory: DirectoryPath,
                                   note_path: NotePath) -> None:
    pass


def _store_history_for_note_delete(notes_directory: DirectoryPath,
                                   note_path: NotePath) -> None:
    pass


def _list_diffs_for_note(notes_directory: DirectoryPath,
                         note_path: NotePath,
                         find_path: ExecutablePath = 'find'
                         ) -> List[NoteDiffTimestamp]:
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

    return [f.split('/')[-1][:-5] for f in diff_files]


def _get_note_diff(notes_directory: DirectoryPath,
                   note_path: NotePath,
                   timestamp: NoteDiffTimestamp) -> NoteDiff:
    return ''
