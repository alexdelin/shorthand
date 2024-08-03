from datetime import datetime, UTC
import logging

import os
import unittest

from shorthand.edit_history import HISTORY_PATH, ensure_daily_starting_version, _list_versions_for_note, _store_history_for_note_edit, _list_diffs_for_note
from utils import setup_environment, teardown_environment, validate_setup


log = logging.getLogger(__name__)


class TestEditHistory(unittest.TestCase):
    """Test Edit History Tools"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.find_path = cls.config['find_path']

    @classmethod
    def teardown_class(cls):
        '''Ensure that we don't leave stamped
        notes around after the tests are run
        '''
        teardown_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_storing_daily_note_version(self):
        for test_note in ['/section/mixed.note', '/bugs.note']:
            ensure_daily_starting_version(notes_directory=self.notes_dir,
                                          note_path=test_note)
            current_utc_day = datetime.now(UTC).date().isoformat()

            # Check the version file was written
            assert os.path.exists(f'{self.notes_dir}/{HISTORY_PATH}/{test_note}/{current_utc_day}.version')

            # Check we can get the version via the API
            note_versions = _list_versions_for_note(
                notes_directory=self.notes_dir,
                note_path=test_note,
                find_path=self.find_path)
            assert note_versions == [current_utc_day]

    def test_storing_edit_diffs(self):
        _store_history_for_note_edit(
            notes_directory=self.notes_dir,
            note_path='/todos.note',
            new_content='foo bar')

        note_versions = _list_versions_for_note(
            notes_directory=self.notes_dir,
            note_path='/todos.note',
            find_path=self.find_path)
        assert len(note_versions) == 1

        note_diffs = _list_diffs_for_note(
            notes_directory=self.notes_dir,
            note_path='/todos.note',
            find_path=self.find_path)
        assert len(note_diffs) == 1
