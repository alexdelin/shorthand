from dataclasses import dataclass
from typing import List, Optional

from shorthand.edit_history import NoteDiffInfo, NoteVersionTimestamp, _list_diffs_for_note, _list_note_versions
from shorthand.types import DirectoryPath, ExecutablePath, NotePath


@dataclass
class EditTimelineEntry:
    version: Optional[NoteVersionTimestamp]
    diffs: List[NoteDiffInfo]

type EditTimeline = List[EditTimelineEntry]


def get_edit_timeline(notes_directory: DirectoryPath,
                      note_path: NotePath,
                      find_path: ExecutablePath = 'find'
                      ) -> EditTimeline:
    '''Get a timeline of the edit history of a note.

       Every entry in the timeline is a note version, and the diffs which
       were applied on top of that note version
    '''
    diffs = _list_diffs_for_note(notes_directory, note_path, find_path)
    versions = _list_note_versions(notes_directory, note_path, find_path)

    diffs.sort(key=lambda x: x['timestamp'], reverse=True)
    versions.sort(reverse=True)

    timeline = []

    for version in versions:
        diffs_for_version = []
        oldest_diff_idx = -1
        for idx, diff in enumerate(diffs):
            if diff['timestamp'] >= version:
                diffs_for_version.append(diff)
                oldest_diff_idx = idx
            else:
                break
        diffs = diffs[oldest_diff_idx + 1:]
        timeline.append(
            EditTimelineEntry(
                version=version, diffs=diffs_for_version))

    if diffs:
        timeline.append(
            # The timeline entry with no version is a placeholder
            # for all of the diffs which were created before the first
            # version existed. This will typically only be a create diff
            EditTimelineEntry(
                version=None, diffs=diffs))

    return timeline



