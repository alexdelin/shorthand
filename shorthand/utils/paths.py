# Path Utilities
import logging


log = logging.getLogger(__name__)


def get_relative_path(notes_directory, path):
    '''Produce a relative path within the notes directory
    from a full path on the filesystem
    '''

    if notes_directory in path:
        path = path[len(notes_directory):]

    return path


def get_display_path(notes_directory, path, directory_filter=None):
    '''Produce a path that is nicer for display than an actual file path
    '''

    path = path.strip('/')

    if directory_filter:
        path = path[len(directory_filter.strip('/')):]

    path = path.strip('/')
    path = ' → '.join(path.split('/'))

    return path
