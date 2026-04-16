import os
import uuid

from shorthand.types import DirectoryPath, FilePath


def do_atomic_file_update(file_path: FilePath, content: str,
                          notes_directory: DirectoryPath) -> None:
    '''Safely update a file on the filesystem via a rename operation.
    '''
    temp_uuid = uuid.uuid4().hex
    temp_dir = f'{notes_directory}/.shorthand/temp'
    temp_file = f'{temp_dir}/{temp_uuid}.temp'

    # Should never happen
    if os.path.exists(temp_file):
        raise ValueError(f'A temp file at {temp_file} already exists!')

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    with open(temp_file, 'w') as f:
        f.write(content)

    os.rename(temp_file, file_path)
