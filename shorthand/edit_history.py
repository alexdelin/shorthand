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
from datetime import datetime
import os
import shutil
import difflib

from shorthand.notes import _get_note
from shorthand.types import DirectoryPath, NotePath, RawNoteContent
from shorthand.utils.paths import get_full_path


DAILY_STARTING_VERSIONS_PATH = '.shorthand/history'
DIFFS_PATH = '.shorthand/diffs'

type Diff = str
'''A git-formatted diff representing the modification made to a note'''


def ensure_daily_starting_version(notes_directory: DirectoryPath,
                                  note_path: NotePath) -> None:
    current_utc_date = datetime.utcnow().date().isoformat()
    daily_starting_version_path = f'{notes_directory}/' + \
                                  f'{DAILY_STARTING_VERSIONS_PATH}/' + \
                                  f'{note_path}/{current_utc_date}.version'

    if os.path.exists(daily_starting_version_path):
        return

    full_note_path = get_full_path(notes_directory, note_path)
    if not os.path.exists(full_note_path):
        raise ValueError(f'Note at path {note_path} does not exist')
    shutil.copy2(full_note_path, daily_starting_version_path)


def calculate_diff_for_edit(notes_directory: DirectoryPath,
                            note_path: NotePath,
                            new_content: RawNoteContent) -> Diff:
    old_content = _get_note(notes_directory, note_path)
    diff_lines = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=note_path, tofile=note_path)
    return ''.join(diff_lines)


def calculate_diff_for_move(old_note_path: NotePath,
                            new_note_path: NotePath) -> Diff:
    # Only works with GNU Patch
    return f'''
    diff --git a/{old_note_path} b/{new_note_path}
    similarity index 100%
    rename from {old_note_path}
    rename to {new_note_path}'''


def calculate_diff_for_create(note_path: NotePath) -> Diff:
    # Only works with GNU Patch
    return f'''
    diff --git a/{note_path} b/{note_path}
    new file mode 100644'''


def calculate_diff_for_delete(notes_directory: DirectoryPath,
                              note_path: NotePath) -> Diff:
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


def store_diff(notes_directory: DirectoryPath, note_path: NotePath,
               diff: Diff) -> None:
    current_utc_time = datetime.utcnow().isoformat(timespec='milliseconds')
    diff_path = f'{notes_directory}/' + \
                f'{DIFFS_PATH}/' + \
                f'{note_path}/{current_utc_time}.diff'
    if os.path.exists(diff_path):
        raise ValueError(f'A diff already exists at path {diff_path}')
    with open(diff_path, 'w') as f:
        f.write(diff)


def store_history_for_note_edit(notes_directory: DirectoryPath,
                                note_path: NotePath,
                                new_content: RawNoteContent) -> None:
    pass


def store_history_for_note_move() -> None:
    pass


def store_history_for_note_create() -> None:
    pass


def store_history_for_note_delete() -> None:
    pass


def list_diffs_for_note() -> None:
    pass


def get_diff() -> Diff:
    pass
