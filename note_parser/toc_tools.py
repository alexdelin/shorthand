import os
import json


def get_toc(notes_directory, directory_filter=None):

    fs_lookup = {}
    ordered_dirs = []
    full_contents = list(os.walk(notes_directory, topdown=False))
    for dir_path, dirnames, filenames in full_contents:

        if '.git' in dir_path:
            continue

        if notes_directory in dir_path:
            dir_path = dir_path[len(notes_directory):]

        notes_filenames = [filename for filename in filenames if filename[-5:] == '.note']

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

        # Modify format to test a frontend library
        # fs_lookup[dir_path]['files'] = [{'text': file, 'icon': 'jstree-file', 'a_attr': {'href': '/render?path=' + dir_path + '/' + file}} for file in fs_lookup[dir_path]['files']]
        # fs_lookup[dir_path]['children'] = fs_lookup[dir_path]['dirs'] + fs_lookup[dir_path]['files']
        # del fs_lookup[dir_path]['dirs']
        # del fs_lookup[dir_path]['files']

    return fs_lookup['']
