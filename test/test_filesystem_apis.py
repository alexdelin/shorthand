import os
import logging

import pytest
import unittest

from shorthand import ShorthandServer

from utils import setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH, setup_logging


log = logging.getLogger(__name__)


class TestFilesystemAPI(unittest.TestCase):
    """Test filesystem API"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']
        cls.patch_path = cls.config['patch_path']
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

    def test_create_file(self):
        self.server.create_file('/newfile.note')
        assert os.path.exists(self.notes_dir + '/newfile.note')

    def test_create_existing_file_fails(self):
        with pytest.raises(ValueError) as e:
            self.server.create_file('/todos.note')
        assert e

    def test_create_directory(self):
        self.server.create_directory('/subdir')
        assert os.path.exists(self.notes_dir + '/subdir')

    def test_create_existing_directory_fails(self):
        with pytest.raises(ValueError) as e:
            self.server.create_directory('/section')
        assert e

    def test_move_file(self):
        self.server.move_file_or_directory('/todos.note', '/todolist.note')
        assert os.path.exists(self.notes_dir + '/todolist.note')

    def test_move_directory(self):
        self.server.move_file_or_directory('/section', '/subdir')
        assert os.path.exists(self.notes_dir + '/subdir/mixed.note')

    def test_move_to_existing_file_fails(self):
        with pytest.raises(ValueError) as e:
            self.server.move_file_or_directory('/todos.note', '/bugs.note')
        assert e

    def test_move_to_existing_directory_fails(self):
        self.server.create_directory('/subdir')
        with pytest.raises(ValueError) as e:
            self.server.move_file_or_directory('/subdir', '/section')
        assert e

    def test_delete_file(self):
        self.server.delete_file('/rec.note')
        assert not os.path.exists(self.notes_dir + '/rec.note')

    def test_delete_missing_file_fails(self):
        with pytest.raises(ValueError) as e:
            self.server.delete_file('/fake.note')
        assert e

    def test_delete_directory(self):
        # Check that non-recursive deltes don't work for directories with content
        with pytest.raises(OSError) as e:
            self.server.delete_directory('/section')
        assert e

        self.server.delete_file('/section/mixed.note')
        self.server.delete_directory('/section')
        assert not os.path.exists(self.notes_dir + '/section')

    def test_delete_directory_recursive(self):
        self.server.delete_directory('/section',recursive=True)
        assert not os.path.exists(self.notes_dir + '/section')

    def test_delete_missing_directory_fails(self):
        with pytest.raises(ValueError) as e:
            self.server.delete_directory('/fake')
        assert e
