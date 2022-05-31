# Shorthand Buffer Management

import os
import logging
from datetime import datetime

from shorthand.notes import _append_to_note


log = logging.getLogger(__name__)


def get_buffer_path(cache_directory: str, buffer_id: str) -> str:
    # Gets the full path on disk to a buffer by its ID.
    # The buffer file is expected to exist or else an error is thrown

    buffer_path = os.path.join(cache_directory, f'{buffer_id}.buffer')

    if not os.path.exists(buffer_path):
        log.warning(f'Buffer file at path {buffer_path} does not exist')
        raise ValueError(f'Buffer ID {buffer_id} not found')

    return buffer_path


def _new_buffer(cache_directory: str) -> str:
    # Creates a new empty buffer and returns the buffer ID

    buffer_id = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    buffer_path = os.path.join(cache_directory, f'{buffer_id}.buffer')

    if os.path.exists(buffer_path):
        raise ValueError(f'Buffer path {buffer_path} already exists, '
                         f'please try again')

    log.info(f'Creating empty buffer at path: {buffer_path}')
    with open(buffer_path, 'w'):
        pass

    return buffer_id


def _get_buffers(cache_directory: str) -> list:
    # Gets a list of the IDs of all buffers which exist

    buffers = []

    # dir_path, subdirs, files = list()
    for file in os.listdir(cache_directory):
        log.debug(file)
        # Length of an ISO Format timestamp with `.buffer` at the end
        if len(file) == 26:
            if file[-7:] == '.buffer':
                buffers.append(file[:-7])

    return buffers


def _get_buffer_content(cache_directory: str, buffer_id: str) -> str:
    # Gets the content of a buffer specified by its ID

    buffer_path = get_buffer_path(cache_directory, buffer_id)

    with open(buffer_path, 'r') as f:
        content = f.read()

    return content


def _update_buffer_content(cache_directory: str, buffer_id: str, content: str) -> bool:
    # Updates the contents of a buffer with the specified content

    buffer_path = get_buffer_path(cache_directory, buffer_id)

    with open(buffer_path, 'w') as f:
        f.write(content)

    return True


def _delete_buffer(cache_directory: str, buffer_id: str) -> bool:
    # Deltes a buffer

    buffer_path = get_buffer_path(cache_directory, buffer_id)
    os.remove(buffer_path)

    return True


def _write_buffer(cache_directory: str, notes_directory: str, buffer_id: str,
                  note_path: str) -> bool:
    # Appends the content of a buffer to the end of a specified note
    # and deletes the buffer

    buffer_content = _get_buffer_content(cache_directory, buffer_id)
    _append_to_note(notes_directory, note_path, buffer_content)

    return True
