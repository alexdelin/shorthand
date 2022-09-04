import os
import json
import logging

from shorthand.utils.paths import get_full_path, is_note_path


log = logging.getLogger(__name__)


IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'svg', 'pdf']


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

    # Handle file not existing
    if not os.path.exists(open_files_path):
        log.info(f'Open Files file {open_files_path} '
                 f'does not exist, creating it')
        with open(open_files_path, 'w') as f:
            json.dump([], f)

    with open(open_files_path, 'r') as f:
        open_files = json.load(f)

    # Manual Type Checking
    if not isinstance(open_files, list):
        log.error(f'Open Files data is not a list')
    if not all([isinstance(x, str) for x in open_files]):
        log.error(f'Open Files data includes an invalid entry')

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
    with open(open_files_path, 'w') as f:
        json.dump([], f)


def open_file(cache_directory, notes_directory, note_path):
    if not is_note_path(notes_directory, note_path):
        log.info(f'Cannot open non-existent file at path: {note_path}')
        return

    open_files_path = f'{cache_directory}/open_files.json'

    with open(open_files_path, 'r') as f:
        open_files = json.load(f)

    if note_path in open_files:
        log.info(f'Note file {note_path} is already open, skipping...')
        return

    open_files.append(note_path)
    log.info(f'Opened file at path: {note_path}')

    with open(open_files_path, 'w') as f:
        json.dump(open_files, f)


def close_file(cache_directory, note_path):
    open_files_path = f'{cache_directory}/open_files.json'

    with open(open_files_path, 'r') as f:
        open_files = json.load(f)

    if note_path not in open_files:
        log.info(f'Note file {note_path} is not open, skipping...')
        return

    open_files.remove(note_path)
    log.info(f'Closed file at path: {note_path}')

    with open(open_files_path, 'w') as f:
        json.dump(open_files, f)
