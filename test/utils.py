import os
import json
import time
import shutil
import logging

import pytest

from shorthand.utils.logging import log_level_from_string, get_handler
from shorthand.utils.config import DEFAULT_LOG_FORMAT


SAMPLE_DATA_DIR = 'sample_data'
TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'
NOTES_DIR = TEMP_DIR + '/notes'
CACHE_DIR = TEMP_DIR + '/cache'
LOG_PATH = TEMP_DIR + '/test.log'
CONFIG_OVERRIDE_PATH = 'config_override.json'
OVERRIDABLE_OPTIONS = ['log_level', 'grep_path', 'find_path']

TEST_CONFIG = {
    "notes_directory": NOTES_DIR,
    "cache_directory": CACHE_DIR,
    "log_file_path": LOG_PATH,
    "log_format": DEFAULT_LOG_FORMAT,
    "log_level": "info",
    "grep_path": "grep",
    "find_path": "find"
}
TEST_CONFIG_PATH = TEMP_DIR + '/config.json'


def get_test_config():
    with open(TEST_CONFIG_PATH, 'r') as f:
        return json.load(f)


def setup_logging(config):
    root_logger = logging.getLogger('shorthand')
    root_logger.handlers.clear()
    handler = get_handler(config)
    root_logger.addHandler(handler)


def validate_setup():
    '''Validate that our test environment was set up correctly
    '''
    if not os.path.exists(TEMP_DIR):
        pytest.skip(f'Temp Directory {TEMP_DIR} does not exist')
    if not os.path.exists(NOTES_DIR):
        pytest.skip(f'Test Notes Directory {NOTES_DIR} does not exist')
    if not os.path.exists(CACHE_DIR):
        pytest.skip(f'Test Cache Directory {CACHE_DIR} does not exist')


def setup_environment():
    '''A utility function to setup the test
    environment before tests are run
    '''
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(CACHE_DIR)
    shutil.copytree(SAMPLE_DATA_DIR, NOTES_DIR)

    # process config overrides
    if os.path.exists(CONFIG_OVERRIDE_PATH):
        with open(CONFIG_OVERRIDE_PATH, 'r') as f:
            config_overrides = json.load(f)
        for key, value in config_overrides.items():
            if key not in OVERRIDABLE_OPTIONS:
                raise ValueError(f'Config option {key} cannot be overridden')
            else:
                TEST_CONFIG[key] = value

    with open(TEST_CONFIG_PATH, 'w') as f:
        json.dump(TEST_CONFIG, f)

    setup_logging(TEST_CONFIG)

    return TEST_CONFIG


def teardown_environment():
    '''A utility function to tear down the test
    environment after tests are run
    '''
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
