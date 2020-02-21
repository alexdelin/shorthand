import os
import re
import unittest

import pytest

from shorthand.utils.rec import load_from_string
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
        with open('rec_data/valid_config.rec', 'r') as f:
            valid_config_data = f.read()
            split_config = re.split(r'#.*?\n', valid_config_data)
            split_config = [config for config in split_config if config]

        for valid_config in split_config:
            record_set = load_from_string(valid_config)
            assert record_set.config.keys()

    def test_invalid_config_parsing(self):
        with open('rec_data/invalid_config.rec', 'r') as f:
            invalid_config_data = f.read()
        split_config = re.split(r'#.*?\n', invalid_config_data)
        split_config = [config for config in split_config if config]

        for invalid_config in split_config:
            with pytest.raises(ValueError) as e:
                record_set = load_from_string(invalid_config)
            assert str(e.value)

    def test_valid_record_parsing(self):
        pass

    def test_invalid_record_parsing(self):
        pass
