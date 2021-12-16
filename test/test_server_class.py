import os
import json
import copy
import logging
import pytest
import unittest

from shorthand import ShorthandServer
from shorthand.utils.config import clean_and_validate_config

from utils import setup_environment, TEMP_DIR, validate_setup, setup_logging


ORIGINAL_CONFIG = setup_environment()
setup_logging(ORIGINAL_CONFIG)
log = logging.getLogger(__name__)

server_config_path = TEMP_DIR + '/server_config.json'
server = None


def write_config(config):
    with open(server_config_path, 'w') as config_file_object:
        json.dump(config, config_file_object)


class TestServerClass(unittest.TestCase):
    """Test the implementation of the ShorthandServer Class"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_setup(self):
        # Write our config to a file that we will use with the server class
        write_config(ORIGINAL_CONFIG)
        assert os.path.exists(server_config_path)

    def test_get_config(self):
        write_config(ORIGINAL_CONFIG)
        server = ShorthandServer(server_config_path)
        assert server.get_config() == clean_and_validate_config(ORIGINAL_CONFIG)

    def test_reload_config(self):
        write_config(ORIGINAL_CONFIG)
        server = ShorthandServer(server_config_path)

        # Make a small but valid change to the config,
        # and ensure it is reflected after reloading
        new_config = copy.deepcopy(ORIGINAL_CONFIG)
        new_config['log_level'] = 'warning'
        write_config(new_config)
        server.reload_config()
        assert server.get_config() == clean_and_validate_config(new_config)

        # Make an invalid change to the config
        bad_config = copy.deepcopy(new_config)
        bad_config['log_level'] = 'foobar'
        write_config(bad_config)
        with pytest.raises(ValueError) as e:
            server.reload_config()
        assert 'Invalid log level' in str(e.value)
        # Ensure the config is not actually updated
        assert server.get_config() == clean_and_validate_config(new_config)

    def test_update_config(self):
        write_config(ORIGINAL_CONFIG)
        server = ShorthandServer(server_config_path)

        # Test a valid update
        update = {
            'log_level': 'WARNING',
            'frontend': {
                'view_history_limit': 500,
                'map_tileserver_url': 'https://{s}.site.com/{z}/{x}/{y}.png'
            }
        }
        server.update_config(update)
        updated_config = server.get_config()
        assert updated_config['log_level'] == update['log_level']
        assert updated_config['frontend'] == update['frontend']

        # Test an invalid update
        bad_update = {
            'log_level': 'INVALID'
        }
        with pytest.raises(ValueError) as e:
            server.update_config(bad_update)
        assert str(e.value)
        assert updated_config['log_level'] == update['log_level']
        assert updated_config['frontend'] == update['frontend']

    def test_save_config(self):
        write_config(ORIGINAL_CONFIG)
        server = ShorthandServer(server_config_path)

        # Test a valid update
        update = {
            'log_level': 'WARNING',
            'frontend': {
                'view_history_limit': 500,
                'map_tileserver_url': 'https://{s}.site.com/{z}/{x}/{y}.png'
            }
        }
        server.update_config(update)
        server.save_config()
        with open(server_config_path, 'r') as config_file_object:
            config = json.load(config_file_object)
        assert config['log_level'] == update['log_level']
        assert config['frontend'] == update['frontend']

    def test_logging(self):
        write_config(ORIGINAL_CONFIG)
        server = ShorthandServer(server_config_path)
        test_message = 'This is just a test message'
        server.log.error(test_message)

        log_file_path = server.config['log_file_path']
        assert os.path.exists(log_file_path)
        with open(log_file_path, 'r') as f:
            log_content = f.read()
        assert log_content
        assert test_message in log_content
