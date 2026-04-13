import os
import shutil
import logging
from typing import List
from datetime import date, datetime, timedelta
from subprocess import PIPE, Popen


from shorthand.notes import _is_note_path
from shorthand.history import HISTORY_PATH
from shorthand.history.types import NoteVersion, NoteVersionTimestamp
from shorthand.types import DirectoryPath, ExecutablePath, NotePath
from shorthand.utils.paths import get_full_path, get_relative_path


log = logging.getLogger(__name__)


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
