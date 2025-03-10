import os
import logging

import pytest

from shorthand.frontend import get_open_files, open_file, close_file, \
                               clear_open_files

from utils import ShorthandTestCase


log = logging.getLogger(__name__)


class TestOpenFilesAPI(ShorthandTestCase):
    """Test tracking Open Files"""

    def corrupt_open_files(self):
        if not os.path.exists(f"{self.notes_dir}/.shorthand/state"):
            os.makedirs(f"{self.notes_dir}/.shorthand/state")
        with open(f"{self.notes_dir}/.shorthand/state/open_files.json", 'w') as f:
            f.write('[')

    def test_get_empty_open_files(self):
        open_files = self.server.get_open_files()
        assert open_files == []
        assert os.path.exists(
            f'{self.notes_dir}/.shorthand/state/open_files.json')

    def test_opening_files(self):
        # Test opening valid paths
        self.server.open_file('/bugs.note')
        open_files = self.server.get_open_files()
        assert '/bugs.note' in open_files

        # Test opening invalid paths
        with pytest.raises(ValueError) as e:
            self.server.open_file('/does-not-exist.note')
        assert 'does not exist' in str(e.value)

        open_files = self.server.get_open_files()
        assert '/does-not-exist.note' not in open_files

    def test_closing_files(self):

        # Open a valid path
        self.server.open_file('/bugs.note')
        self.server.open_file('/todos.note')
        open_files = self.server.get_open_files()
        assert set(['/bugs.note', '/todos.note']) == set(open_files)

        # Close the open file
        self.server.close_file('/bugs.note')
        open_files = self.server.get_open_files()
        assert '/bugs.note' not in open_files

        # Test handling for closing a file that isn't open
        self.server.close_file('/notopen.note')
        open_files = self.server.get_open_files()
        assert ['/todos.note'] == open_files

    def test_clearing_open_files(self):

        # Open a valid path
        self.server.open_file('/bugs.note')
        self.server.open_file('/todos.note')
        self.server.open_file('/rec.note')
        open_files = self.server.get_open_files()
        assert set(['/bugs.note', '/rec.note', '/todos.note']
                  ) == set(open_files)

        self.server.clear_open_files()
        open_files = self.server.get_open_files()
        assert open_files == []

    def test_handling_corrupt_open_file_list(self):
        # Test get operation with corrupted open files
        self.corrupt_open_files()
        open_files = self.server.get_open_files()
        assert open_files == []

        # Test open operation with corrupted open files
        self.corrupt_open_files()
        self.server.open_file('/todos.note')
        open_files = self.server.get_open_files()
        assert open_files == ['/todos.note']

        # Test close operation with corrupted open files
        self.corrupt_open_files()
        self.server.close_file('/todos.note')
        open_files = self.server.get_open_files()
        assert open_files == []

        # Test clear operation with corrupted open files
        self.corrupt_open_files()
        self.server.clear_open_files()
        open_files = self.server.get_open_files()
        assert open_files == []

    def test_deleting_an_open_file(self):
        self.server.open_file('/todos.note')
        self.server.delete_file('/todos.note')
        open_files = self.server.get_open_files()
        assert open_files == []
