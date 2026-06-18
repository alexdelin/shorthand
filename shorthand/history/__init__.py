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
import logging
from datetime import datetime, UTC, timedelta
from subprocess import PIPE, Popen

from shorthand.history.diffs import _list_diffs_for_note, _get_note_diff, calculate_diff_for_create, calculate_diff_for_delete, calculate_diff_for_edit, calculate_diff_for_move, delete_diff, get_unified_diff, save_diff
from shorthand.history.patching import apply_diffs
from shorthand.history.versions import add_note_version_for_move, ensure_note_version, note_version_exists_for_date
from shorthand.notes import _get_note, _is_note_path
from shorthand.types import DirectoryPath, ExecutablePath, NotePath, RawNoteContent, Subdir
from shorthand.utils.paths import get_full_path, get_relative_path


MERGE_CUTOFF_LIMIT_MIN = 15


log = logging.getLogger(__name__)


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
