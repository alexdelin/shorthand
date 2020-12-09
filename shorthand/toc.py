import os
import logging


log = logging.getLogger(__name__)


def _get_toc(notes_directory, directory_filter=None):

    fs_lookup = {}
    ordered_dirs = []
    full_contents = list(os.walk(notes_directory, topdown=False))
    for dir_path, dirnames, filenames in full_contents:

        if '.git' in dir_path:
            continue

        if notes_directory in dir_path:
            dir_path = dir_path[len(notes_directory):]

        notes_filenames = [filename
                           for filename in filenames
                           if filename[-5:] == '.note']

        fs_lookup[dir_path] = {
            'files': notes_filenames,
            'dirs': dirnames,
            'path': dir_path,
            'text': dir_path.split('/')[-1]
        }
        ordered_dirs.append(dir_path)

    for dir_path in ordered_dirs:

        populated_subdirs = []
        for subdir in fs_lookup[dir_path]['dirs']:

            if subdir == '.git':
                continue

            subdir_full_path = dir_path + '/' + subdir
            subdir_data = fs_lookup[subdir_full_path]
            populated_subdirs.append(subdir_data)

        fs_lookup[dir_path]['dirs'] = populated_subdirs

    # Everything ends up nested under an empty key
    toc = fs_lookup['']

    return toc
