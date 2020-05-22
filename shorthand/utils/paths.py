# Path Utilities
import logging


log = logging.getLogger(__name__)


def get_relative_path(notes_directory, path):
    '''Produce a relative path within the notes directory
    from a full path on the filesystem
    '''

    if not path:
        raise ValueError('No Path provided!')

    # Always work with paths that start with slashes, and
    # Directory filters that start with slashes and do not end
    # with slashes
    if path[0] != '/':
        path = '/' + path

    # Remove notes directory location from the start of the path
    if notes_directory[0] != '/':
        notes_directory = '/' + notes_directory
    if notes_directory[-1] == '/':
        notes_directory = notes_directory[:-1]
    if notes_directory == path[:len(notes_directory)]:
        path = path[len(notes_directory):]

    return path


def get_display_path(path, directory_filter=None):
    '''Produce a path that is nicer for display than an actual file path
    If a directory filter is specified, it produces a path that is relative
    to that directory
    '''

    if isinstance(directory_filter, str):
        if not directory_filter.strip('/'):
            raise ValueError(f'Invalid directory filter '\
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
