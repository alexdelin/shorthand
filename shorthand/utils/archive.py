from io import BytesIO
import tarfile

from shorthand.types import DirectoryPath


def _get_note_archive(notes_directory: DirectoryPath) -> bytes:
    buffer = BytesIO()
    with tarfile.open(None, "w:xz", preset=9, fileobj=buffer) as tar:
        tar.add(notes_directory, arcname='archive')
    return buffer.getvalue()

