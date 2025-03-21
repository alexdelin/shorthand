# Shorthand Buffer Management

import os
import logging
from datetime import UTC, datetime
from typing import List

from shorthand.notes import _append_to_note
from shorthand.types import DirectoryPath, NotePath


log = logging.getLogger(__name__)


type BufferID = str
'''The ID for a buffer. The format is an ISO-8601 timestamp
   of the UTC timestamp when the buffer was first created'''

type BufferContent = str
'''The raw text content of a buffer'''


def get_buffers_dir(notes_directory: DirectoryPath) -> DirectoryPath:
    return f'{notes_directory}/.shorthand/buffers'


def get_buffer_path(notes_directory: DirectoryPath, buffer_id: BufferID) -> str:
    # Gets the full path on disk to a buffer by its ID.
    # The buffer file is expected to exist or else an error is thrown

    buffer_path = f'{get_buffers_dir(notes_directory)}/{buffer_id}.buffer'

    if not os.path.exists(buffer_path):
        log.warning(f'Buffer file at path {buffer_path} does not exist')
        raise ValueError(f'Buffer ID {buffer_id} not found')

    return buffer_path


def _new_buffer(notes_directory: DirectoryPath) -> BufferID:
    # Creates a new empty buffer and returns the buffer ID

    buffers_dir = get_buffers_dir(notes_directory)

    if not os.path.exists(buffers_dir):
        os.makedirs(buffers_dir)

    buffer_id = datetime.now(UTC).isoformat(timespec='milliseconds')
    buffer_path = f'{get_buffers_dir(notes_directory)}/{buffer_id}.buffer'

    if os.path.exists(buffer_path):
        raise ValueError(f'Buffer path {buffer_path} already exists, ' + \
                         f'please try again')

    log.info(f'Creating empty buffer at path: {buffer_path}')
    with open(buffer_path, 'w'):
        pass

    return buffer_id


def _list_buffers(notes_directory: DirectoryPath) -> List[BufferID]:
    # Gets a list of the IDs of all buffers which exist

    buffers = []
    buffers_dir = get_buffers_dir(notes_directory)

    if not os.path.exists(buffers_dir):
        os.makedirs(buffers_dir)
        return []

    for file in os.listdir(buffers_dir):
        # Length of an ISO Format timestamp with `.buffer` at the end
        if len(file) == 36 and file[-7:] == '.buffer':
            buffers.append(file[:-7])

    return buffers


def _get_buffer_content(notes_directory: DirectoryPath, buffer_id: BufferID) -> BufferContent:
    # Gets the content of a buffer specified by its ID

    buffer_path = get_buffer_path(notes_directory, buffer_id)

    with open(buffer_path, 'r') as f:
        content = f.read()

    return content


def _update_buffer_content(notes_directory: DirectoryPath, buffer_id: BufferID, content: BufferContent) -> None:
    # Updates the contents of a buffer with the specified content

    buffer_path = get_buffer_path(notes_directory, buffer_id)

    with open(buffer_path, 'w') as f:
        f.write(content)


def _delete_buffer(notes_directory: DirectoryPath, buffer_id: BufferID) -> None:
    # Deltes a buffer

    buffer_path = get_buffer_path(notes_directory, buffer_id)
    os.remove(buffer_path)


def _write_buffer(notes_directory: DirectoryPath, buffer_id: BufferID,
                  note_path: NotePath) -> None:
    # Appends the content of a buffer to the end of a specified note
    # and deletes the buffer

    buffer_content = _get_buffer_content(notes_directory, buffer_id)
    _append_to_note(notes_directory, note_path, buffer_content)
