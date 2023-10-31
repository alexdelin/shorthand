from typing import Union

# System level concepts
# ---------------------

# An absolute path to a file on the local filesystem
FilePath = str

# An absolute path to an executable file on the local filesystem
ExecutablePath = str

# An absolute path to a directory on the local filesystem (with no trailing slash)
DirectoryPath = str


# Notes directory level concepts
# ------------------------------

# An absolute path to a note from the root of the notes directory
NotePath = str

# An absolute path to a non-note file from the root of the notes directory
ResourcePath = str

# An absolute path to any file from the root of the notes directory
InternalAbsoluteFilePath = Union[NotePath, ResourcePath]

# An absolute path to a subdirectory within the notes directory
Subdir = str

# An absolute path to any file or directory from the root of the notes directory
InternalAbsolutePath = Union[InternalAbsoluteFilePath, Subdir]

# A nicely formatted version of a note path
DisplayPath = str

# A relative path to a note from another note.
# Typically must be transformed into a NotePath before it can be used
RelativeNotePath = str

# A relative path to a resource from a note.
# Typically must be transformed into a ResourcePath before it can be used
RelativeResourcePath = str

# A relative path from a note to another file
InternalRelativeFilePath = Union[RelativeNotePath, RelativeResourcePath]

# A relative path within the notes directory to a subdir
RelativeDirectoryPath = str

# A relative path from a note to either a file or directory
InternalRelativePath = Union[InternalRelativeFilePath, RelativeDirectoryPath]


# Note level concepts
# -------------------

# The full raw string content of a note
RawNoteContent = str

# The full raw conntent of a single line in a note
RawNoteLine = str

# A URL which points to an external resource
ExternalURL = str


# API level concepts
# ------------------
ACKResponse = str

CSVData = str

JSONShorthandConfig = str
JSONShorthandConfigUpdates = str
JSONSearchResults = str
JSONTOC = str
JSONSubdirs = str
JSONLinks = str
