import os
import json
import time
import shutil
import logging

import pytest

from shorthand.utils.logging import log_level_from_string, get_handler
from shorthand.utils.config import DEFAULT_LOG_FORMAT, ShorthandConfig


SAMPLE_DATA_DIR = 'sample_data'
TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'
NOTES_DIR = TEMP_DIR + '/notes'
LOG_PATH = TEMP_DIR + '/test.log'
CONFIG_OVERRIDE_PATH = 'config_override.json'
OVERRIDABLE_OPTIONS = ['log_level', 'grep_path', 'find_path']

TEST_CONFIG: ShorthandConfig = {
    "notes_directory": NOTES_DIR,
    "log_file_path": LOG_PATH,
    "log_format": DEFAULT_LOG_FORMAT,
    "log_level": "info",
    "grep_path": "grep",
    "find_path": "find",
    "default_directory": None,
    "frontend": {
        "view_history_limit": 1,
        "map_tileserver_url": 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    }
}
TEST_CONFIG_PATH = TEMP_DIR + '/config.json'


def get_test_config() -> ShorthandConfig:
    with open(TEST_CONFIG_PATH, 'r') as f:
        return json.load(f)


def setup_logging(config: ShorthandConfig) -> None:
    root_logger = logging.getLogger('shorthand')
    if root_logger.handlers:
        for h in root_logger.handlers:
            h.close()
        root_logger.handlers.clear()
    handler = get_handler(config)
    root_logger.addHandler(handler)


def validate_setup() -> None:
    '''Validate that our test environment was set up correctly
    '''
    if not os.path.exists(TEMP_DIR):
        pytest.skip(f'Temp Directory {TEMP_DIR} does not exist')
    if not os.path.exists(NOTES_DIR):
        pytest.skip(f'Test Notes Directory {NOTES_DIR} does not exist')


def setup_environment() -> ShorthandConfig:
    '''A utility function to setup the test
    environment before tests are run
    '''
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
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


def teardown_environment() -> None:
    '''A utility function to tear down the test
    environment after tests are run
    '''
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
