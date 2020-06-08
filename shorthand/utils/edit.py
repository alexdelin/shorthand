import logging

from shorthand.utils.paths import get_full_path


log = logging.getLogger(__name__)


def update_note(notes_directory, file_path, content):
    '''Update an existing note with the full contents provided
    '''

    # Ensure that we have the full path even if
    # a relative path is specified
    full_path = get_full_path(notes_directory, file_path)

    with open(full_path, 'w') as note_file:
        note_file.write(content)


def append_to_note():
    '''Append the specified content to an existing note
    '''
    raise NotImplementedError('Not implemented yet!')


def create_note():
    '''Create a new note
    '''
    raise NotImplementedError('Not implemented yet!')
