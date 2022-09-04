import os
import unittest

from shorthand.frontend import get_open_files, open_file, close_file, \
                               clear_open_files

from utils import setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH, setup_logging, get_test_config


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

    def test_get_empty_open_files(self):
        test_config = get_test_config()
        open_files = get_open_files(test_config['cache_directory'],
                                    test_config['notes_directory'])
        assert open_files == []
        assert os.path.exists(
            f'{test_config["cache_directory"]}/open_files.json')

    def test_opening_files(self):
        test_config = get_test_config()

        # Test opening valid paths
        open_file(test_config['cache_directory'],
                  test_config['notes_directory'],
                  '/bugs.note')
        open_files = get_open_files(test_config['cache_directory'],
                                    test_config['notes_directory'])
        assert '/bugs.note' in open_files

        # Test opening invalid paths
        open_file(test_config['cache_directory'],
                  test_config['notes_directory'],
                  '/does-not-exist.note')
        open_files = get_open_files(test_config['cache_directory'],
                                    test_config['notes_directory'])
        assert '/does-not-exist.note' not in open_files
