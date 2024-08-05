import os
import json
import copy
import logging
import pytest
import unittest

from shorthand import ShorthandServer
from shorthand.utils.config import clean_and_validate_config

from utils import setup_environment, TEMP_DIR, validate_setup


log = logging.getLogger(__name__)


class TestServerClass(unittest.TestCase):
    """Test the implementation of the ShorthandServer Class"""

    def write_config(self, config):
        with open(self.server_config_path, 'w') as config_file_object:
            json.dump(config, config_file_object)

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']
        cls.server_config_path = TEMP_DIR + '/server_config.json'

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()
        self.write_config(self.config)
        self.server = ShorthandServer(self.server_config_path)

    def test_setup(self):
        # Write our config to a file that we will use with the server class
        assert os.path.exists(self.server_config_path)

    def test_get_config(self):
        assert self.server.get_config() == clean_and_validate_config(self.config)

    def test_reload_config(self):
        # Make a small but valid change to the config,
        # and ensure it is reflected after reloading
        new_config = copy.deepcopy(self.config)
        new_config['log_level'] = 'warning'
        self.write_config(new_config)
        self.server.reload_config()
        assert self.server.get_config() == clean_and_validate_config(new_config)

        # Make an invalid change to the config
        bad_config = copy.deepcopy(new_config)
        bad_config['log_level'] = 'foobar'
        self.write_config(bad_config)
        with pytest.raises(ValueError) as e:
            self.server.reload_config()
        assert 'Invalid log level' in str(e.value)
        # Ensure the config is not actually updated
        assert self.server.get_config() == clean_and_validate_config(new_config)

    def test_update_config(self):
        # Test a valid update
        update = {
            'log_level': 'WARNING',
            'frontend': {
                'view_history_limit': 500,
                'map_tileserver_url': 'https://{s}.site.com/{z}/{x}/{y}.png'
            }
        }
        self.server.update_config(update)
        updated_config = self.server.get_config()
        assert updated_config['log_level'] == update['log_level']
        assert updated_config['frontend'] == update['frontend']

        # Test an invalid update
        bad_update = {
            'log_level': 'INVALID'
        }
        with pytest.raises(ValueError) as e:
            self.server.update_config(bad_update)
        assert str(e.value)
        assert updated_config['log_level'] == update['log_level']
        assert updated_config['frontend'] == update['frontend']

    def test_save_config(self):
        # Test a valid update
        update = {
            'log_level': 'WARNING',
            'frontend': {
                'view_history_limit': 500,
                'map_tileserver_url': 'https://{s}.site.com/{z}/{x}/{y}.png'
            }
        }
        self.server.update_config(update)
        self.server.save_config()
        with open(self.server_config_path, 'r') as config_file_object:
            config = json.load(config_file_object)
        assert config['log_level'] == update['log_level']
        assert config['frontend'] == update['frontend']

    def test_logging(self):
        test_message = 'This is just a test message'
        self.server.log.error(test_message)

        log_file_path = self.server.config['log_file_path']
        assert os.path.exists(log_file_path)
        with open(log_file_path, 'r') as f:
            log_content = f.read()
        assert log_content
        assert test_message in log_content
