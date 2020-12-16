import codecs
import logging

from shorthand.utils.paths import get_full_path


log = logging.getLogger(__name__)


def _get_note(notes_directory, path):
    '''Get the full raw content of a note as a string
    given:
        - The full path to the notes directory
        - Its path, as a relative path
          within the notes directory
    '''

    full_path = get_full_path(notes_directory, path)

    with open(full_path, 'r') as note_file_object:
        note_content = note_file_object.read()

    return note_content


def _update_note(notes_directory, file_path, content):
    '''Update an existing note with the full contents provided
    '''

    # Ensure that we have the full path even if
    # a relative path is specified
    full_path = get_full_path(notes_directory, file_path)

    with open(full_path, 'w') as note_file:
        note_file.write(content)


def _append_to_note():
    '''Append the specified content to an existing note
    '''
    raise NotImplementedError('Not implemented yet!')


def _create_note():
    '''Create a new note
    '''
    raise NotImplementedError('Not implemented yet!')
