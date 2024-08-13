import os
import logging

import pytest

from shorthand.edit_timeline import get_edit_timeline
from shorthand.types import InternalAbsolutePath
from utils import ShorthandTestCase


log = logging.getLogger(__name__)


class TestEditHistory(ShorthandTestCase):
    """Test Edit History Tools"""

    def create_history_file(self, path: InternalAbsolutePath):
        target_file = self.notes_dir + path
        if not os.path.exists(os.path.dirname(target_file)):
            os.makedirs(os.path.dirname(target_file))
        with open(target_file, 'w') as f:
            pass

    def test_getting_edit_timeline(self):
        # Create some shell version and diff history
        self.create_history_file('/.shorthand/history/todos.note/2024-08-07T00:00:00.000+00:00.version')
        self.create_history_file('/.shorthand/history/todos.note/2024-08-11T00:00:00.000+00:00.version')
        self.create_history_file('/.shorthand/history/todos.note/2024-08-11T14:21:33.178+00:00.version')

        self.create_history_file('/.shorthand/history/todos.note/diffs/2024/08/06/2024-08-06T01:54:23.789+00:00.create.diff')
        self.create_history_file('/.shorthand/history/todos.note/diffs/2024/08/07/2024-08-07T01:54:23.789+00:00.edit.diff')
        self.create_history_file('/.shorthand/history/todos.note/diffs/2024/08/11/2024-08-11T08:29:23.789+00:00.edit.diff')
        self.create_history_file('/.shorthand/history/todos.note/diffs/2024/08/11/2024-08-11T17:29:23.789+00:00.edit.diff')

        # Check that the timeline has the right content
        timeline = get_edit_timeline(
            notes_directory=self.notes_dir, note_path='/todos.note',
            find_path=self.find_path)
        assert len(timeline) == 4
        for entry in timeline:
            assert len(entry.diffs) == 1
            if entry.version:
                assert entry.diffs[0]['timestamp'] > entry.version
