import os
import shutil
from pathlib import Path


SAMPLE_DATA_DIR = 'sample_data'
TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'
NOTES_DIR = TEMP_DIR + '/notes'
CACHE_DIR = TEMP_DIR + '/cache'
LOG_PATH = TEMP_DIR + '/test.log'

TEST_CONFIG = {
    "notes_directory": NOTES_DIR,
    "cache_directory": CACHE_DIR,
    "log_file_path": LOG_PATH,
    "log_level": "debug",
    "grep_path": "/usr/local/bin/ggrep"
}


def setup_environment():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(CACHE_DIR)
        Path(CACHE_DIR + '/recent_files.txt').touch()
        shutil.copytree(SAMPLE_DATA_DIR, NOTES_DIR)
    return TEST_CONFIG
