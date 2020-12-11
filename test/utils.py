import os
import json
import shutil
# from pathlib import Path


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
    "log_level": "info",
    "grep_path": "grep",
    "find_path": "find"
}


def setup_environment():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(CACHE_DIR)
        # Path(CACHE_DIR + '/recent_files.txt').touch()
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

    return TEST_CONFIG
