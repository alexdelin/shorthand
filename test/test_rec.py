import unittest

from utils import setup_environment
from model import NoteparserModel


CONFIG = setup_environment()
MODEL = NoteparserModel()


class TestRec(unittest.TestCase):
    '''Basic tests for recfile parsing
    '''

    def test_setup(self):
        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_valid_config_parsing(self):
        pass

    def test_invalid_config_parsing(self):
        pass

    def test_valid_record_parsing(self):
        pass

    def test_invalid_record_parsing(self):
        pass
