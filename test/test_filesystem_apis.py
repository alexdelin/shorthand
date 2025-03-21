import os
import logging

import pytest

from utils import ShorthandTestCase


log = logging.getLogger(__name__)


class TestFilesystemAPI(ShorthandTestCase):
    """Test filesystem API"""

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
