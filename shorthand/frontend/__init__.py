import os
import logging

from shorthand.utils.paths import get_full_path


log = logging.getLogger(__name__)


IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'svg', 'pdf']


def is_image_path(notes_directory, path):
    # Check the file extension
    extension = path.split('.')[-1]
    if extension not in IMAGE_FILE_EXTENSIONS:
        return False

    # Check that the specified file actually exists
    full_path = get_full_path(notes_directory, path)
    if not os.path.exists(full_path):
        return False

    return True
