import os
import logging

import pytest
import unittest

from shorthand.frontend import get_open_files, open_file, close_file, \
                               clear_open_files

from utils import setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH, setup_logging


log = logging.getLogger(__name__)


class TestOpenFilesAPI(unittest.TestCase):
    """Test tracking Open Files"""

    def corrupt_open_files(self):
        with open(f"{self.notes_dir}/.shorthand/state/open_files.json", 'w') as f:
            f.write('[')

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
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
        clear_open_files(self.notes_dir)

    def test_get_empty_open_files(self):
        open_files = get_open_files(self.notes_dir)
        assert open_files == []
        assert os.path.exists(
            f'{self.notes_dir}/.shorthand/state/open_files.json')

    def test_opening_files(self):
        # Test opening valid paths
        open_file(self.notes_dir, '/bugs.note')
        open_files = get_open_files(self.notes_dir)
        assert '/bugs.note' in open_files

        # Test opening invalid paths
        with pytest.raises(ValueError) as e:
            open_file(self.notes_dir, '/does-not-exist.note')
        assert 'non-existent file' in str(e.value)

        open_files = get_open_files(self.notes_dir)
        assert '/does-not-exist.note' not in open_files

    def test_closing_files(self):

        # Open a valid path
        open_file(self.notes_dir, '/bugs.note')
        open_file(self.notes_dir, '/todos.note')
        open_files = get_open_files(self.notes_dir)
        assert set(['/bugs.note', '/todos.note']) == set(open_files)

        # Close the open file
        close_file(self.notes_dir, '/bugs.note')
        open_files = get_open_files(self.notes_dir)
        assert '/bugs.note' not in open_files

        # Test handling for closing a file that isn't open
        close_file(self.notes_dir, '/notopen.note')
        open_files = get_open_files(self.notes_dir)
        assert ['/todos.note'] == open_files

    def test_clearing_open_files(self):

        # Open a valid path
        open_file(self.notes_dir, '/bugs.note')
        open_file(self.notes_dir, '/todos.note')
        open_file(self.notes_dir, '/rec.note')
        open_files = get_open_files(self.notes_dir)
        assert set(['/bugs.note', '/rec.note', '/todos.note']
                  ) == set(open_files)

        clear_open_files(self.notes_dir)
        open_files = get_open_files(self.notes_dir)
        assert open_files == []

    def test_handling_corrupt_open_file_list(self):
        # Test get operation with corrupted open files
        self.corrupt_open_files()
        open_files = get_open_files(self.notes_dir)
        assert open_files == []

        # Test open operation with corrupted open files
        self.corrupt_open_files()
        open_file(self.notes_dir, '/todos.note')
        open_files = get_open_files(self.notes_dir)
        assert open_files == ['/todos.note']

        # Test close operation with corrupted open files
        self.corrupt_open_files()
        close_file(self.notes_dir, '/todos.note')
        open_files = get_open_files(self.notes_dir)
        assert open_files == []

        # Test clear operation with corrupted open files
        self.corrupt_open_files()
        clear_open_files(self.notes_dir)
        open_files = get_open_files(self.notes_dir)
        assert open_files == []
