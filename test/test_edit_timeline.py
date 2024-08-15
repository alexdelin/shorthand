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

    def test_timeline_for_create_diffs(self):
        self.server.create_file('/new.note')
        timeline = self.server.get_edit_timeline('/new.note')
        assert timeline
        assert len(timeline) == 1
        assert not timeline[0].version
        assert len(timeline[0].diffs) == 1

    def test_timeline_for_edit_diffs(self):
        self.server.update_note('/todos.note', 'New Content')
        timeline = self.server.get_edit_timeline('/todos.note')
        assert timeline
        assert len(timeline) == 1
        assert timeline[0].version
        assert len(timeline[0].diffs)
        # Check that the day components of the version and diff timestamps match
        assert timeline[0].diffs[0]['timestamp'][:10] == timeline[0].version[:10]

    def test_timeline_for_move_diffs(self):
        self.server.move_file_or_directory('/todos.note', '/new.note')

        timeline_1 = self.server.get_edit_timeline('/todos.note')
        assert len(timeline_1) == 1
        assert timeline_1[0].version

        timeline_2 = self.server.get_edit_timeline('/new.note')
        assert len(timeline_2) == 1
        assert not timeline_2[0].version

        # Check both move diffs have the same timestamp
        assert timeline_1[0].diffs[0]['timestamp'] == timeline_2[0].diffs[0]['timestamp']

    def test_timeline_for_move_with_second_version(self):
        self.server.update_note('/todos.note', 'New Content')
        self.server.delete_file('/todos.note')
        self.server.move_file_or_directory('/bugs.note', '/todos.note')

        timeline = self.server.get_edit_timeline('/todos.note')
        assert len(timeline) == 2
        assert timeline[0].version
        assert '00:00:00.000' not in timeline[0].version
        assert len(timeline[0].diffs) == 0

        assert len(timeline[1].diffs) == 3
        assert set([d['diff_type'] for d in timeline[1].diffs]) == set(['edit', 'delete', 'move'])


    def test_timeline_for_delete_diffs(self):
        self.server.delete_file('/todos.note')
        timeline = self.server.get_edit_timeline('/todos.note')
        assert timeline
        assert len(timeline) == 1
        assert timeline[0].version
        assert len(timeline[0].diffs)
        # Check that the day components of the version and diff timestamps match
        assert timeline[0].diffs[0]['timestamp'][:10] == timeline[0].version[:10]
