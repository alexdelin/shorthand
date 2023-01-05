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

# A nicely formatted
DisplayPath = str

# A relative path to a note from another note.
# Typically must be transformed into a NotePath before it can be used
RelativeNotePath = str

# A relative path within the notes directory to a subdir
RelativeDirectoryPath = str

# A subdirectory within the notes directory
Subdir = str


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