import os
import json
import logging

from shorthand.utils.paths import get_full_path, is_note_path


log = logging.getLogger(__name__)


IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'svg', 'pdf']


def _ensure_file_exists(file_path, default_content):
    ''' Utility to handle file not existing
        If a file exist at the specified path, do nothing
        If not, create a file populated with the default
          contents, dumped as a JSON string
    '''
    if not os.path.exists(file_path):
        log.info(f'Open Files file {file_path} '
                 f'does not exist, creating it')
        with open(file_path, 'w') as f:
            json.dump(default_content, f)


def is_image_path(notes_directory, path):
    # Check the file extension
    extension = path.split('.')[-1]
    if extension not in IMAGE_FILE_EXTENSIONS:
        return False

    # Check that the specified file actually exists
    full_path = get_full_path(notes_directory, path)
    if not os.path.exists(full_path):
        return False

    return True


def get_open_files(cache_directory, notes_directory):
    open_files_path = f'{cache_directory}/open_files.json'
    _ensure_file_exists(open_files_path, [])

    with open(open_files_path, 'r') as f:
        open_files = json.load(f)

    # Manual Type Checking
    if not isinstance(open_files, list):
        raise ValueError(f'Open Files data is not a list')
    if not all([isinstance(x, str) for x in open_files]):
        raise ValueError(f'Open Files data includes an invalid entry')

    # Check that all files actually exist
    found_invalid_paths = False
    for note in open_files:
        if not is_note_path(notes_directory, note):
            found_invalid_paths = True
            log.info(f'Found invalid open file path: {note}, '
                     f'removing...')
            close_file(cache_directory, note)

    # Re-read open files if we found invalid paths
    #   that we had to remove
    if found_invalid_paths:
        with open(open_files_path, 'r') as f:
            open_files = json.load(f)

    return open_files


def clear_open_files(cache_directory):
    open_files_path = f'{cache_directory}/open_files.json'
    _ensure_file_exists(open_files_path, [])

    with open(open_files_path, 'w') as f:
        json.dump([], f)

    return 'ack'


def open_file(cache_directory, notes_directory, note_path):
    if not is_note_path(notes_directory, note_path):
        raise ValueError(f'Cannot open non-existent file at path: {note_path}')

    open_files_path = f'{cache_directory}/open_files.json'
    _ensure_file_exists(open_files_path, [])

    with open(open_files_path, 'r') as f:
        open_files = json.load(f)

    if open_files and note_path == open_files[-1]:
        log.info(f'Note file {note_path} is already the most '
                 f'recently opened file, nothing to do...')
        return 'ack'
    if note_path in open_files:
        open_files.remove(note_path)

    open_files.append(note_path)
    log.info(f'Opened file at path: {note_path}')

    with open(open_files_path, 'w') as f:
        json.dump(open_files, f)

    return 'ack'


def close_file(cache_directory, note_path):
    open_files_path = f'{cache_directory}/open_files.json'
    _ensure_file_exists(open_files_path, [])

    with open(open_files_path, 'r') as f:
        open_files = json.load(f)

    if note_path not in open_files:
        log.info(f'Note file {note_path} is not open, skipping...')
        return 'ack'

    open_files.remove(note_path)
    log.info(f'Closed file at path: {note_path}')

    with open(open_files_path, 'w') as f:
        json.dump(open_files, f)

    return 'ack'
