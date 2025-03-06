from typing import Literal, Union

# System level concepts
# ---------------------

type FilePath = str
'''An absolute path to a file on the local filesystem

   Example: `/etc/shorthand/shorthand_config.json`
'''

type ExecutablePath = str
'''An absolute path to an executable file on the local filesystem

   Example: `/usr/bin/grep`
'''

type DirectoryPath = str
'''An absolute path to a directory on the local filesystem (with no trailing slash)

   Example: `/var/lib/notes`
'''

# Notes directory level concepts
# ------------------------------

type NotePath = str
'''An absolute path to a note from the root of the notes directory

   Example: `/subdir/todos.note`
'''

type ResourcePath = str
'''An absolute path to a non-note file from the root of the notes directory

   Example: `/subdir/image.jpeg`
'''

type InternalAbsoluteFilePath = Union[NotePath, ResourcePath]
'''An absolute path to any file from the root of the notes directory

   Example: `/subdir/todos.note`
   Example: `/subdir/image.jpeg`
'''

type Subdir = str
'''An absolute path to a subdirectory within the notes directory

   Example: `/subdir/nested`
'''

type InternalAbsolutePath = Union[InternalAbsoluteFilePath, Subdir]
'''An absolute path to any file or directory from the root of the notes directory

   Example: `/subdir/todos.note`
   Example: `/subdir/image.jpeg`
   Example: `/subdir/nested`
'''

type DisplayPath = str
'''A nicely formatted version of a note path

   Example: `subdir -> todos.note`
'''

type RelativeNotePath = str
'''A relative path to a note from another note.
   Typically must be transformed into a NotePath before it can be used

   Example: `../subdir/todos.note`
'''

type RelativeResourcePath = str
'''A relative path to a resource from a note.
   Typically must be transformed into a ResourcePath before it can be used

   Example: `../subdir/image.jpeg`
'''

type InternalRelativeFilePath = Union[RelativeNotePath, RelativeResourcePath]
'''A relative path from a note to another file

   Example: `../subdir/todos.note`
   Example: `../subdir/image.jpeg`
'''

type RelativeDirectoryPath = str
'''A relative path within the notes directory to a subdir

   Example: `../subdir`
'''

type InternalRelativePath = Union[InternalRelativeFilePath, RelativeDirectoryPath]
'''A relative path from a note to either a file or directory

   Example: `../subdir/todos.note`
   Example: `../subdir/image.jpeg`
   Example: `../subdir`
'''


# Note level concepts
# -------------------

type RawNoteContent = str
'''The full raw string content of a note'''

type RawNoteLine = str
'''The full raw conntent of a single line in a note'''

type ExternalURL = str
'''A URL which points to an external resource'''

type RawResourceContent = bytes
'''Raw binary content of a resource'''

# API level concepts
# ------------------
type ACKResponse = Literal["ack"]

type CSVData = str

type JSONShorthandConfig = str
type JSONShorthandConfigUpdates = str
type JSONSearchResults = str
type JSONTOC = str
type JSONSubdirs = str
type JSONLinks = str
