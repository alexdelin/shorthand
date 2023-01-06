# Path Utilities
import os
import logging
from typing import Optional, Union

from shorthand.types import DirectoryPath, DisplayPath, ExternalURL, \
                            FilePath, NotePath, RelativeNotePath, Subdir


log = logging.getLogger(__name__)


def get_relative_path(notes_directory: DirectoryPath, path: FilePath
                      ) -> NotePath:
    '''Produce a relative path within the notes directory
    from a full path on the filesystem
    '''

    if not path:
        raise ValueError('No Path provided!')

    # Always work with paths that start with slashes
    # and do not end with slashes
    if path[0] != '/':
        path = '/' + path
    if notes_directory[0] != '/':
        notes_directory = '/' + notes_directory
    if notes_directory[-1] == '/':
        notes_directory = notes_directory[:-1]

    # Remove notes directory location from the start of the path
    if notes_directory == path[:len(notes_directory)]:
        path = path[len(notes_directory):]

    return path


def get_full_path(notes_directory: DirectoryPath, relative_path: NotePath
                  ) -> FilePath:
    '''Get a full path on the local filesystem from a
    relative path
    '''

    if not relative_path:
        raise ValueError('No path provided!')

    if notes_directory in relative_path:
        # We already have a full path
        return relative_path

    # Always work with paths that start with slashes
    # and do not end with slashes
    if notes_directory[0] != '/':
        notes_directory = '/' + notes_directory
    if notes_directory[-1] == '/':
        notes_directory = notes_directory[:-1]
    if relative_path[0] != '/':
        relative_path = '/' + relative_path

    return notes_directory + relative_path


def get_display_path(path: NotePath, directory_filter: Optional[str] = None
                     ) -> DisplayPath:
    '''Produce a path that is nicer for display than an actual file path
    If a directory filter is specified, it produces a path that is relative
    to that directory
    '''

    if isinstance(directory_filter, str):
        if not directory_filter.strip('/'):
            raise ValueError(f'Invalid directory filter '
                             f'{directory_filter} specified')

    # Always work with paths that start with slashes, and
    # Directory filters that start with slashes and do not end
    # with slashes
    if path[0] != '/':
        path = '/' + path

    # Remove directory filter from start of the remaining path
    if directory_filter:
        if directory_filter[0] != '/':
            directory_filter = '/' + directory_filter
        if directory_filter[-1] == '/':
            directory_filter = directory_filter[:-1]
        if directory_filter == path[:len(directory_filter)]:
            path = path[len(directory_filter):]

    # Change slashes to arrows to make the path easier to look at
    path = path.strip('/')
    path = ' → '.join(path.split('/'))

    return path


def _get_subdirs(notes_directory: DirectoryPath, max_depth: int = 2,
                 exclude_hidden=True
                 ) -> list[Subdir]:
    '''Returns a list of all sub-directories within the notes directory
       up to the specified depth.
    '''
    all_directories = []
    for subdir in os.walk(notes_directory):
        subdir_path = subdir[0][len(notes_directory) + 1:]
        if not subdir_path:
            continue
        elif exclude_hidden and subdir_path.startswith('.'):
            continue
        elif len(subdir_path.split('/')) > max_depth:
            continue
        else:
            all_directories.append(subdir_path)
    return all_directories


def parse_relative_link_path(source: NotePath,
                             target: Union[NotePath, RelativeNotePath,
                                           ExternalURL]
                             ) -> Union[NotePath, ExternalURL]:
    '''Transform a relative path from a source note to a relative
       path within the notes directory

       source: Path within the notes directory to the link source
       target: Relative path from source note to target
    '''

    # Handle external links
    if is_external_path(target):
        return target

    # Handle if the target is not actually a relative path
    if target.startswith('/'):
        return target

    # Check that source is a full relative path
    if not source.startswith('/'):
        raise ValueError(f'Invalid Source note {source}')

    source_dir = os.path.dirname(source)
    target_path = os.path.join(source_dir, target)
    # Note: os.normpath will prevent you from breaking out of
    #       the notes_directory via lots of ../../..
    target_path = os.path.normpath(target_path)
    return target_path


def is_external_path(path: Union[NotePath, RelativeNotePath, ExternalURL]
                     ) -> bool:
    '''Determines whether or not a given path point to an external
       web page or an internal note (within the notes directory).
       Paths to internal notes can be either relative or absolute
       paths within the notes directory
    '''
    if path.startswith('http://') or path.startswith('https://'):
        return True
    else:
        return False


def is_note_path(notes_directory: DirectoryPath, path: NotePath) -> bool:
    '''consumes a note path and ensures whether a note exists at that path.
       Ignores any #element tag after the filename

       notes_directory: full path to the root of the notes directory
       path: relateive path of the note within the notes directory
    '''
    if '#' in path:
        path = path.split('#')[0]

    full_path = get_full_path(notes_directory, path)
    return os.path.exists(full_path)
