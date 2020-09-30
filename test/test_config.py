import os
import logging
import pytest
import unittest

from shorthand.utils.logging import setup_logging
from shorthand.utils.config import clean_and_validate_config, \
    DEFAULT_CACHE_DIR, DEFAULT_LOG_FILE, DEFAULT_LOG_LEVEL, \
    DEFAULT_GREP_PATH, DEFAULT_FIND_PATH, DEFAULT_FRONTEND_CONFIG

from utils import setup_environment
from model import ShorthandModel


ORIGINAL_CONFIG = setup_environment()
setup_logging(ORIGINAL_CONFIG)
log = logging.getLogger(__name__)
MODEL = ShorthandModel()

CONFIG_FIELDS = ['notes_directory', 'cache_directory', 'default_directory',
                 'log_file_path', 'log_level', 'grep_path', 'find_path',
                 'frontend']
FRONTEND_CONFIG_FIELDS = ['view_history_limit', 'map_tileserver_url']


class TestConfig(unittest.TestCase):
    """Test configuration management utilities"""

    def test_setup(self):

        test_dir = ORIGINAL_CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_basic_config_validation(self):
        cleaned_config = clean_and_validate_config(ORIGINAL_CONFIG)
        # Check basic format of cleaned config
        assert isinstance(cleaned_config, dict)
        assert len(cleaned_config.keys()) > 0
        # Ensure all expected top-level fields are present
        assert all([field in cleaned_config for field in CONFIG_FIELDS])
        # Ensure no extra top-level fields are included
        assert all([field in CONFIG_FIELDS for field in cleaned_config])

    def test_required_config_fields(self):

        # Test that config missing required fields raises an error
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({})
        assert 'Missing required field' in str(e.value)

        # Test that config with ONLY required fields is accepted
        default_config = clean_and_validate_config({
            "notes_directory": ORIGINAL_CONFIG['notes_directory']
        })

        # Test that all default values are respected
        assert default_config['cache_directory'] == DEFAULT_CACHE_DIR
        assert default_config['log_file_path'] == DEFAULT_LOG_FILE
        assert default_config['log_level'] == DEFAULT_LOG_LEVEL
        assert default_config['grep_path'].endswith(DEFAULT_GREP_PATH)
        assert default_config['find_path'].endswith(DEFAULT_FIND_PATH)
        assert default_config['frontend'] == DEFAULT_FRONTEND_CONFIG

    def test_path_cleaning(self):
        cleaned_config = clean_and_validate_config({
            "notes_directory": ORIGINAL_CONFIG['notes_directory'] + '/',
            "cache_directory": ORIGINAL_CONFIG['cache_directory'] + '/'
        })
        assert cleaned_config['notes_directory'][-1] != '/'
        assert cleaned_config['notes_directory'][0] == '/'
        assert cleaned_config['cache_directory'][-1] != '/'
        assert cleaned_config['cache_directory'][0] == '/'

    def test_path_validation(self):
        # Specify an invalid path and ensure it raises an error
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": "foo"
            })
        assert 'does not exist' in str(e.value)
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "cache_directory": "foo"
            })
        assert 'does not exist' in str(e.value)

    def test_logging_config(self):
        # Test an invalid log level being specified
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "log_level": 'foo'
            })
        assert 'Invalid log level' in str(e.value)

        # Test that all valid log levels are respected
        for level in ['NOTSET', 'DEBUG', 'INFO',
                      'WARNING', 'ERROR', 'CRITICAL']:
            cleaned_config = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "log_level": level
            })
            assert cleaned_config['log_level'] == level

    def test_default_dir_validation(self):
        # Test that a valid default dir is accepted
        cleaned_config = clean_and_validate_config({
            "notes_directory": ORIGINAL_CONFIG['notes_directory'],
            "default_directory": "section"
        })
        assert cleaned_config['default_directory'] == 'section'

        # Test that an invalid default dir throws an error
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "default_directory": "foo"
            })
        assert 'does not exist within notes directory' in str(e.value)

    def test_utility_path_validation(self):
        # Test using the name of each executable
        _ = clean_and_validate_config({
            "notes_directory": ORIGINAL_CONFIG['notes_directory'],
            "grep_path": "grep",
            "find_path": "find"
        })

        # Test invalid names
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "grep_path": "asdfghjkl",
                "find_path": "find"
            })
        assert 'could not be located' in str(e.value)

        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "grep_path": "grep",
                "find_path": "lkjhgfdsa"
            })
        assert 'could not be located' in str(e.value)

        # Test an invalid full path
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "grep_path": "/path/that/doesnt/exist",
                "find_path": "find"
            })
        assert 'could not be located' in str(e.value)

        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "grep_path": "grep",
                "find_path": "/path/that/doesnt/exist"
            })
        assert 'could not be located' in str(e.value)

    def test_frontend_config(self):
        pass
