import logging
from subprocess import PIPE, Popen
import tempfile
from typing import List

from shorthand.history.types import NoteDiff
from shorthand.types import ExecutablePath, RawNoteContent


log = logging.getLogger(__name__)


def apply_diffs(starting_content: RawNoteContent,
                diffs: List[NoteDiff],
                patch_path: ExecutablePath = 'patch',
                reverse: bool = False) -> RawNoteContent:
    '''Apply one or more patches to a file with GNU patch

       Patches are applied in the order they are provided

       If `reverse` is set, then patches are undone from the starting content
    '''

    # Remove empty patches from being applied,
    # because it will cause patch to return an error code
    filtered_diffs = [d for d in diffs if '---' in d]
    if not filtered_diffs:
        return starting_content

    with tempfile.TemporaryDirectory() as tmpdir:
        original_filename = f'{tmpdir}/original.txt'
        patched_filename = f'{tmpdir}/patched.txt'
        diff_filenames = []

        with open(original_filename, 'w') as f:
            f.write(starting_content)
            if not starting_content.endswith('\n'):
                f.write('\n')

        for idx, diff_content in enumerate(filtered_diffs):
            diff_filename = f'{tmpdir}/diff_{idx}.txt'
            with open(diff_filename, 'w') as f:
                f.write(diff_content)
                if not starting_content.endswith('\n'):
                    f.write('\n')
            diff_filenames.append(diff_filename)

        patch_command = f'{patch_path} {original_filename}'
        if reverse:
            patch_command += ' -R'
        for diff in diff_filenames:
            patch_command += f' -i {diff}'
        patch_command += f' -o {patched_filename}'

        log.warning(f'Running command {patch_command} to apply diffs')
        proc = Popen(patch_command, stdout=PIPE, stderr=PIPE, shell=True)
        output, err = proc.communicate()
        status_code = proc.returncode

        if status_code > 1:
            raise ValueError(f'Error while calculating diff {output.decode()} {err.decode()}')

        with open(patched_filename, 'r') as f:
            return f.read()
