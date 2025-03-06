import os

from shorthand.utils.paths import _is_resource_path
from shorthand.types import DirectoryPath, RawResourceContent, ResourcePath
from shorthand.utils.paths import get_full_path


def _get_resource(notes_directory: DirectoryPath, resource_path: ResourcePath
                  ) -> RawResourceContent:
    '''Get the full raw content of a resource as byes given:
        - The full path to the notes directory
        - Its path, as a relative path
          within the notes directory
    '''

    if not _is_resource_path(notes_directory, resource_path, must_exist=True):
        raise ValueError(f'Valid resource not found at path {resource_path}')

    full_path = get_full_path(notes_directory, resource_path)
    with open(full_path, 'rb') as note_file_object:
        note_content = note_file_object.read()

    return note_content
