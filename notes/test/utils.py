import os
import shutil


SAMPLE_DATA_DIR = 'sample_data'
TEMP_DIR = os.path.dirname(os.path.realpath(__file__)) + '/temp'

TEST_CONFIG = {
    "notes_directory": TEMP_DIR
}


def setup_environment():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    shutil.copytree(SAMPLE_DATA_DIR, TEMP_DIR)
    return TEST_CONFIG
