import os
import re
import unittest

import pytest

from shorthand.utils.rec import load_from_string
from utils import setup_environment


CONFIG = setup_environment()


class TestRecConfig(unittest.TestCase):
    '''Basic tests for recfile config parsing
    '''

    def test_setup(self):
        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_valid_config_parsing(self):
        with open('rec_data/valid_config.rec', 'r') as f:
            valid_config_data = f.read()
        split_config = re.split(r'#.*?\n', valid_config_data)
        split_config = [config for config in split_config if config.strip()]

        for valid_config in split_config:
            record_set = load_from_string(valid_config)
            assert record_set.config.keys()

    def test_invalid_config_parsing(self):
        with open('rec_data/invalid_config.rec', 'r') as f:
            invalid_config_data = f.read()
        split_config = re.split(r'#.*?\n', invalid_config_data)
        split_config = [config for config in split_config if config.strip()]

        for invalid_config in split_config:
            with pytest.raises(ValueError) as e:
                record_set = load_from_string(invalid_config)
            assert str(e.value)


class TestRecConfig(unittest.TestCase):
    '''Basic tests for recfile record set parsing
    '''

    def test_valid_record_parsing(self):
        with open('rec_data/valid_records.rec', 'r') as f:
            valid_record_data = f.read()
        valid_record_sets = re.split(r'#.*?\n', valid_record_data)
        valid_record_sets = [record_set for record_set in valid_record_sets if record_set.strip()]
        for valid_record_set in valid_record_sets:
            loaded_record_set = load_from_string(valid_record_set)
            assert loaded_record_set.records

    def test_invalid_record_parsing(self):
        with open('rec_data/invalid_records.rec', 'r') as f:
            invalid_record_data = f.read()
        invalid_record_sets = re.split(r'#.*?\n', invalid_record_data)
        invalid_record_sets = [record_set for record_set in invalid_record_sets if record_set.strip()]
        for invalid_record_set in invalid_record_sets:
            with pytest.raises(ValueError) as e:
                loaded_record_set = load_from_string(invalid_record_set)
            assert str(e.value)

