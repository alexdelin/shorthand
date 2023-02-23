import os
import logging

import pytest
import unittest

from shorthand.frontend import get_open_files, open_file, close_file, \
                               clear_open_files

from utils import setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH, setup_logging


CONFIG = setup_environment()
log = logging.getLogger(__name__)


class TestOpenFilesAPI(unittest.TestCase):
    """Test tracking Open Files"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

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
        clear_open_files(CONFIG['cache_directory'])

    def test_get_empty_open_files(self):
        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert open_files == []
        assert os.path.exists(
            f'{CONFIG["cache_directory"]}/open_files.json')

    def test_opening_files(self):
        # Test opening valid paths
        open_file(CONFIG['cache_directory'],
                  CONFIG['notes_directory'],
                  '/bugs.note')
        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert '/bugs.note' in open_files

        # Test opening invalid paths
        with pytest.raises(ValueError) as e:
            open_file(CONFIG['cache_directory'],
                      CONFIG['notes_directory'],
                      '/does-not-exist.note')
        assert 'non-existent file' in str(e.value)

        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert '/does-not-exist.note' not in open_files

    def test_closing_files(self):

        # Open a valid path
        open_file(CONFIG['cache_directory'],
                  CONFIG['notes_directory'],
                  '/bugs.note')
        open_file(CONFIG['cache_directory'],
                  CONFIG['notes_directory'],
                  '/todos.note')
        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert set(['/bugs.note', '/todos.note']) == set(open_files)

        # Close the open file
        close_file(CONFIG['cache_directory'],
                   '/bugs.note')
        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert '/bugs.note' not in open_files

        # Test handling for closing a file that isn't open
        close_file(CONFIG['cache_directory'],
                   '/notopen.note')
        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert ['/todos.note'] == open_files

    def test_clearing_open_files(self):

        # Open a valid path
        open_file(CONFIG['cache_directory'],
                  CONFIG['notes_directory'],
                  '/bugs.note')
        open_file(CONFIG['cache_directory'],
                  CONFIG['notes_directory'],
                  '/todos.note')
        open_file(CONFIG['cache_directory'],
                  CONFIG['notes_directory'],
                  '/rec.note')
        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert set(['/bugs.note', '/rec.note',
                    '/todos.note']) == set(open_files)

        clear_open_files(CONFIG['cache_directory'])
        open_files = get_open_files(CONFIG['cache_directory'],
                                    CONFIG['notes_directory'])
        assert open_files == []
