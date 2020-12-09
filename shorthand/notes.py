import codecs
import logging

from shorthand.utils.paths import get_full_path


log = logging.getLogger(__name__)


def get_file_content(file_path):
    '''Get the raw unmodified contents of a
    note file
    #TODO - Re-work this so it only accepts a relative
    path within the notes directory
    '''

    with codecs.open(file_path, mode='r', encoding="utf-8") as file_object:
        file_content = file_object.read()

    return file_content


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
