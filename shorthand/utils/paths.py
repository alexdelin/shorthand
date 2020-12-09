# Path Utilities
import logging


log = logging.getLogger(__name__)


def get_relative_path(notes_directory, path):
    '''Produce a relative path within the notes directory
    from a full path on the filesystem
    #TODO - Add a server class method for this
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


def get_full_path(notes_directory, relative_path):
    '''Get a full path on the local filesystem from a
    relative path
    #TODO - Add a server class method for this
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


def get_display_path(path, directory_filter=None):
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
