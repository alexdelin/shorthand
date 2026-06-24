'''
Master Edit Timeline - A summary of all changes across the entire notes directory over time
			           Only summary information for each diff is returned.
For a view of the history of a single note over time, see Edit Timeline
'''

import logging
from subprocess import PIPE, Popen
from typing import Dict, List, TypedDict

from shorthand.history.types import HISTORY_PATH, NoteDiffInfo
from shorthand.history.diffs import extract_paths_from_move_diff
from shorthand.utils.paths import get_relative_path
from shorthand.types import DirectoryPath, ExecutablePath, ISOFormatDate
from shorthand.history import _get_note_diff


log = logging.getLogger(__name__)


class MasterEditTimelineDayDetails(TypedDict):
    count: int
    diffs: List[NoteDiffInfo]

type MasterEditTimeline = Dict[ISOFormatDate, MasterEditTimelineDayDetails]


def get_master_edit_timeline(notes_directory: DirectoryPath,
                             find_path: ExecutablePath = 'find') -> MasterEditTimeline:
	
    find_command = f'{find_path} {notes_directory}/' + \
                   f'{HISTORY_PATH} ' + \
                   '-type f -name "*.diff"'

    log.debug(f'Running command {find_command} to list note diffs')
    proc = Popen(find_command, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = proc.communicate()
    output_lines = output.decode().split('\n')

    diff_files = [get_relative_path(notes_directory, line.strip())
                  for line in output_lines
                  if line.strip()]

    move_diff_keys = []
    all_diffs: List[NoteDiffInfo] = []
    for diff_file in diff_files:
        note_path = diff_file.split('/diffs/')[0].split(HISTORY_PATH)[1]
        filename = diff_file.split('/')[-1]
        diff_type = filename.split('.')[-2]
        timestamp = filename.rsplit('.', 2)[0]
        if diff_type == 'move':
            full_diff = _get_note_diff(notes_directory, note_path, timestamp, diff_type)
            move_diff_paths = extract_paths_from_move_diff(full_diff)
            # Move diffs will show up twice, so only include one copy of each
            if note_path != move_diff_paths['from']:
                continue
            all_diffs.append({
                'diff_type': diff_type,
                'timestamp': timestamp,
                'note_path': note_path,
                'from_path': move_diff_paths['from'],
                'to_path': move_diff_paths['to']
            })
        else:
            all_diffs.append({
                'diff_type': diff_type,
                'note_path': note_path,
                'timestamp': timestamp
            })

    all_diffs.sort(key=lambda x: x['timestamp'], reverse=True)

    diffs_by_day = {}
    for diff in all_diffs:
        date = diff['timestamp'][:10]
        diffs_by_day.setdefault(date, {'diffs': []})
        diffs_by_day[date]['diffs'].append(diff)

    for date, summary in diffs_by_day.items():
        summary['count'] = len(summary['diffs'])

    return diffs_by_day
