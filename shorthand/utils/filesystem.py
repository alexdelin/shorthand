import os
import shutil
import logging

from shorthand.types import DirectoryPath, Subdir, InternalAbsoluteFilePath, InternalAbsolutePath
from shorthand.utils.paths import _is_note_path, get_full_path


log = logging.getLogger(__name__)


def _create_file(notes_directory: DirectoryPath,
                 file_path: InternalAbsoluteFilePath
                 ) -> None:
    '''Create a new empty file at a specific internal path
    '''
    full_path = get_full_path(notes_directory, file_path)

    if os.path.exists(full_path):
        raise ValueError(f'File to create at path {file_path} already exists')

    with open(full_path, 'w') as f:
        pass


def _upload_resource(notes_directory: DirectoryPath,
                     path: InternalAbsoluteFilePath,
                     content: bytes,
                     allow_overwrite: bool = False
                     ) -> None:
    '''Create a new resource file at a specific internal path
       with the specified content
    '''
    if _is_note_path(notes_directory, path, must_exist=False):
        raise ValueError('Cannot upload a resource with a note file extension')

    full_path = get_full_path(notes_directory, path)
    log.warning(f'Uploading resource to {full_path}')
    if not allow_overwrite:
        if os.path.exists(full_path):
            raise ValueError(f'Cannot create resource, a file ' +
                             f'already exists at path {path}')

    with open(full_path, 'wb') as f:
        f.write(content)


def _move_file_or_directory(notes_directory: DirectoryPath,
                            source: InternalAbsolutePath,
                            destination: InternalAbsolutePath
                            ) -> None:
    '''Move a file or directory from a source path to a destination path
    '''
    full_source_path = get_full_path(notes_directory, source)
    full_destination_path = get_full_path(notes_directory, destination)

    if not os.path.exists(full_source_path):
        raise ValueError(f'File to move at path {source} does not exist')
    if os.path.exists(full_destination_path):
        raise ValueError(f'Target for move at path {destination} already exists')

    shutil.move(full_source_path, full_destination_path)


def _delete_file(notes_directory: DirectoryPath,
                 file_path: InternalAbsoluteFilePath
                 ) -> None:
    '''Delete a file off the filesystem
    '''
    full_path = get_full_path(notes_directory, file_path)

    if not os.path.exists(full_path):
        raise ValueError(f'File to delete at path {file_path} does not exist')

    os.remove(full_path)


def _create_directory(notes_directory: DirectoryPath,
                      directory_path: Subdir
                      ) -> None:
    '''Create a subdirectory within the notes directory. Will create
       any needed parent dirs if they don't already exist
    '''
    if not directory_path:
        raise ValueError('No path provided for new directory to create')

    full_path = get_full_path(notes_directory, directory_path)

    if os.path.exists(full_path):
        raise ValueError(f'Directory to create at path {directory_path} already exists')

    os.makedirs(full_path)


def _delete_directory(notes_directory: DirectoryPath, directory_path: Subdir,
                      recursive: bool = False
                      ) -> None:
    '''Delete an empty subdirectory within the notes directory.
       If recursive is set to True, will delete all of the contents as well
    '''
    full_path = get_full_path(notes_directory, directory_path)

    if not os.path.exists(full_path):
        raise ValueError(f'Directory to delete at path {directory_path} does not exist')

    if recursive:
        shutil.rmtree(full_path)
    else:
        os.rmdir(full_path)
