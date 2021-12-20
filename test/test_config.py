import logging
import pytest
import unittest

from shorthand.utils.config import clean_and_validate_config, \
    _modify_config, DEFAULT_CACHE_DIR, DEFAULT_LOG_FILE, \
    DEFAULT_LOG_LEVEL, DEFAULT_GREP_PATH, DEFAULT_FIND_PATH, \
    DEFAULT_FRONTEND_CONFIG, DEFAULT_CONFIG

from utils import setup_environment, validate_setup, setup_logging


ORIGINAL_CONFIG = setup_environment()
setup_logging(ORIGINAL_CONFIG)
log = logging.getLogger(__name__)


class TestConfig(unittest.TestCase):
    """Test configuration management utilities"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_basic_config_validation(self):
        cleaned_config = clean_and_validate_config(ORIGINAL_CONFIG)
        # Check basic format of cleaned config
        assert isinstance(cleaned_config, dict)
        assert len(cleaned_config.keys()) > 0
        # Ensure all expected top-level fields are present
        assert all([field in cleaned_config
                    for field in DEFAULT_CONFIG.keys()])
        # Ensure no extra top-level fields are included
        assert all([field in DEFAULT_CONFIG.keys()
                    for field in cleaned_config])

        frontend_config = cleaned_config.get('frontend')
        # Ensure all expected frontend fields are present
        assert all([field in frontend_config
                    for field in DEFAULT_FRONTEND_CONFIG.keys()])
        # Ensure no extra frontend fields are included
        assert all([field in DEFAULT_FRONTEND_CONFIG.keys()
                    for field in frontend_config])

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
        for level in ['DEBUG', 'INFO', 'WARNING',
                      'ERROR', 'CRITICAL']:
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

        # Test Passing Valid config
        cleaned_config = clean_and_validate_config({
            "notes_directory": ORIGINAL_CONFIG['notes_directory'],
            "frontend": DEFAULT_FRONTEND_CONFIG
        })
        assert cleaned_config['frontend'] == DEFAULT_FRONTEND_CONFIG

        # Test that if only a single field is included, the rest are
        # added with defaults
        for field in DEFAULT_FRONTEND_CONFIG.keys():
            cleaned_config = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "frontend": {
                    field: DEFAULT_FRONTEND_CONFIG[field]
                }
            })
            assert cleaned_config['frontend'][field] == \
                DEFAULT_FRONTEND_CONFIG[field]
            frontend_config = cleaned_config.get('frontend')
            # Ensure all expected frontend fields are present
            assert set(frontend_config.keys()) == \
                set(DEFAULT_FRONTEND_CONFIG.keys())

        # Test an integer view history limit
        _ = clean_and_validate_config({
            "notes_directory": ORIGINAL_CONFIG['notes_directory'],
            "frontend": {
                "view_history_limit": 5
            }
        })

        # Test a string view history limit
        _ = clean_and_validate_config({
            "notes_directory": ORIGINAL_CONFIG['notes_directory'],
            "frontend": {
                "view_history_limit": '37'
            }
        })

        # Test an invalid view history limit
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "frontend": {
                    "view_history_limit": "foo"
                }
            })
        assert 'Can\'t convert view history limit value of' in str(e.value)

        # Test an invalid map tileserver URL
        with pytest.raises(ValueError) as e:
            _ = clean_and_validate_config({
                "notes_directory": ORIGINAL_CONFIG['notes_directory'],
                "frontend": {
                    "map_tileserver_url": "foo"
                }
            })
        assert 'Map Tileserver URL must be a valid URL' == str(e.value)

    def test_valid_config_updates(self):

        config = clean_and_validate_config(ORIGINAL_CONFIG)
        updates = {
            'log_level': 'WARNING',
            'frontend': {
                'view_history_limit': 500,
                'map_tileserver_url': 'https://{s}.site.com/{z}/{x}/{y}.png'
            }
        }
        config = _modify_config(config, updates)
        assert config['log_level'] == updates['log_level']
        assert config['frontend'] == updates['frontend']

    def test_invalid_config_updates(self):

        config = clean_and_validate_config(ORIGINAL_CONFIG)

        updates = {
            'log_level': 'INVALID'
        }
        with pytest.raises(ValueError) as e:
            _ = _modify_config(config, updates)
        assert str(e.value)

        updates = {
            'frontend': {
                'view_history_limit': 'foo'
            }
        }
        with pytest.raises(ValueError) as e:
            _ = _modify_config(config, updates)
        assert str(e.value)
