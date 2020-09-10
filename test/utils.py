import os
import shutil


SAMPLE_DATA_DIR = 'sample_data'
TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'
LOG_PATH = os.path.dirname(os.path.realpath(__file__)) + '/test.log'

TEST_CONFIG = {
    "notes_directory": TEMP_DIR,
    "log_file_path": LOG_PATH,
    "log_level": "debug",
    "grep_path": "/usr/local/bin/ggrep"
}


def setup_environment():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    shutil.copytree(SAMPLE_DATA_DIR, TEMP_DIR)
    return TEST_CONFIG
