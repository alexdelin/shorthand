
from typing import Literal, Required, TypedDict

from shorthand.types import NotePath


HISTORY_PATH = '.shorthand/history'


type NoteDiff = str
'''A git-formatted diff representing a modification made to a note'''

type NoteDiffTimestamp = str
'''An ISO-8601 timestamp for the UTC time that a note was modified
   with millisecond-precision. Includes the `+00:00` UTC timezone offset'''

type NoteDiffType = Literal['create', 'edit', 'move', 'delete']
'''Options for types of changes which can be recorded as diffs'''

class NoteDiffInfo(TypedDict, total=False):
    diff_type: Required[NoteDiffType]
    timestamp: Required[NoteDiffTimestamp]
    from_path: NotePath
    to_path: NotePath
    move_direction: Literal['in', 'out']

type NoteVersion = str
'''The raw note content of a historical version of a note,
   as of the start of a given UTC day'''

type NoteVersionTimestamp = str
'''An ISO-8601 time stamp for the UTC time that a version was created
   with millisecond-precision. Includes the `+00:00` UTC timezone offset

   By default, this is the timestamp of the start of day UTC time'''
