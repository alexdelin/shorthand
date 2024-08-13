import logging

import os
import unittest

import pytest

from shorthand import ShorthandServer
from shorthand.edit_timeline import get_edit_timeline
from shorthand.types import InternalAbsolutePath
from utils import TEST_CONFIG_PATH, setup_environment, teardown_environment, validate_setup


log = logging.getLogger(__name__)


class TestEditHistory(unittest.TestCase):
    """Test Edit History Tools"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']
        cls.server = ShorthandServer(TEST_CONFIG_PATH)

    @classmethod
    def teardown_class(cls):
        '''Ensure that we don't leave stamped
        notes around after the tests are run
        '''
        teardown_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        setup_environment()
        validate_setup()

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




