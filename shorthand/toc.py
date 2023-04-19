import os
import logging
from typing import TypedDict

from shorthand.types import DirectoryPath, RelativeDirectoryPath


log = logging.getLogger(__name__)


class TOC(TypedDict):
    files: list[str]
    dirs: list["TOC"]
    path: RelativeDirectoryPath
    text: str


def _get_toc(notes_directory: DirectoryPath) -> TOC:
    '''Get a TOC object
    '''

    fs_lookup = {}
    ordered_dirs = []
    full_contents = list(os.walk(notes_directory, topdown=False))
    for dir_path, dirnames, filenames in full_contents:

        # Skip all hidden folders
        if '/.' in dir_path:
            continue

        if notes_directory in dir_path:
            dir_path = dir_path[len(notes_directory):]

        notes_filenames = [filename
                           for filename in filenames
                           if filename[-5:] == '.note']
        notes_filenames.sort()
        dirnames.sort()

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

            if subdir[0] == '.':
                continue

            subdir_full_path = dir_path + '/' + subdir
            subdir_data = fs_lookup[subdir_full_path]
            populated_subdirs.append(subdir_data)

        fs_lookup[dir_path]['dirs'] = populated_subdirs

    # Everything ends up nested under an empty key
    toc = fs_lookup['']

    return toc
