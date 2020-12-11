import os
import re
import json
import logging
import unittest

import pytest

from shorthand.utils.logging import setup_logging
from shorthand.elements.record_sets import _get_record_set, _get_record_sets
from shorthand.utils.rec import load_from_string
from utils import setup_environment


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestRecConfig(unittest.TestCase):
    '''Basic tests for recfile config parsing
    '''

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
                _ = load_from_string(invalid_config)
            assert str(e.value)


class TestRecordParsing(unittest.TestCase):
    '''Basic tests for recfile record set parsing
    '''

    def test_valid_record_parsing(self):
        with open('rec_data/valid_records.rec', 'r') as f:
            valid_record_data = f.read()
        valid_record_sets = re.split(r'#.*?\n', valid_record_data)
        valid_record_sets = [record_set
                             for record_set in valid_record_sets
                             if record_set.strip()]
        for valid_record_set in valid_record_sets:
            loaded_record_set = load_from_string(valid_record_set)
            assert loaded_record_set.records

    def test_invalid_record_parsing(self):
        with open('rec_data/invalid_records.rec', 'r') as f:
            invalid_record_data = f.read()
        invalid_record_sets = re.split(r'#.*?\n', invalid_record_data)
        invalid_record_sets = [record_set
                               for record_set in invalid_record_sets
                               if record_set.strip()]
        for invalid_record_set in invalid_record_sets:
            with pytest.raises(ValueError) as e:
                _ = load_from_string(invalid_record_set)
            assert str(e.value)


class TestRecordLoad(unittest.TestCase):
    """Test Loading new records into a record set"""

    def test_load_csv_no_pk(self):
        '''Test importing data from a CSV file into a
        record set with no primary key field set
        '''
        with open('rec_data/base_config_no_pk.rec', 'r') as f:
            base_record_set_raw = f.read()
        record_set = load_from_string(base_record_set_raw)

        with open('rec_data/import_data.csv', 'r') as f:
            csv_data = f.read()
        record_set.insert_csv(csv_data)

        assert len(record_set.records) == 6

    def test_load_csv_with_pk(self):
        '''Test importing data from a CSV file into a
        record set with a primary key field set
        '''
        with open('rec_data/base_config_with_pk.rec', 'r') as f:
            base_record_set_raw = f.read()
        record_set = load_from_string(base_record_set_raw)

        with open('rec_data/import_data.csv', 'r') as f:
            csv_data = f.read()
        record_set.insert_csv(csv_data)

        assert len(record_set.records) == 5

    def test_load_json_no_pk(self):
        '''Test importing data from a JSON file into a
        record set with no primary key field set
        '''
        with open('rec_data/base_config_no_pk.rec', 'r') as f:
            base_record_set_raw = f.read()
        record_set = load_from_string(base_record_set_raw)

        with open('rec_data/import_data.json', 'r') as f:
            csv_data = f.read()
        record_set.insert_json(csv_data)

        assert len(record_set.records) == 6

    def test_load_json_with_pk(self):
        '''Test importing data from a JSON file into a
        record set with a primary key field set
        '''
        with open('rec_data/base_config_with_pk.rec', 'r') as f:
            base_record_set_raw = f.read()
        record_set = load_from_string(base_record_set_raw)

        with open('rec_data/import_data.json', 'r') as f:
            csv_data = f.read()
        record_set.insert_json(csv_data)

        assert len(record_set.records) == 5


class TestRecordExport(unittest.TestCase):
    """Test Exporting a record set to various formats"""

    def test_loading_record_set(self):
        '''Load a record set to test exports of in later tests
        '''

        with open('rec_data/export_test.rec', 'r') as f:
            record_data = f.read()
        record_set = load_from_string(record_data)
        assert len(record_set.records) == 2

    def test_json_export(self):
        '''Test exporting a record set to JSON format
        '''
        with open('rec_data/export_test.rec', 'r') as f:
            record_data = f.read()
        record_set = load_from_string(record_data)
        exported_record_set = [
            {"Id": [0], "A": ["test"], "B": ["test"]},
            {"Id": [1], "A": ["test"], "B": ["test"]}
        ]
        self.assertCountEqual(json.loads(record_set.get_json()),
                              exported_record_set)

    def test_csv_export(self):
        '''Test exporting a record set to CSV format
        '''
        with open('rec_data/export_test.rec', 'r') as f:
            record_data = f.read()
        record_set = load_from_string(record_data)
        assert record_set.get_csv() == 'Id,A,B\r\n'\
                                       '0,test,test\r\n'\
                                       '1,test,test\r\n'

    def test_rec_export(self):
        '''Test exporting a record set to rec format
        '''

        # Test exporting with config included
        # Test exporting with config excluded
        with open('rec_data/export_test.rec', 'r') as f:
            record_data = f.read()
        record_set = load_from_string(record_data)
        assert record_set.get_rec() == 'Id: 0\nA: test\nB: test\n\n'\
                                       'Id: 1\nA: test\nB: test'


class TestFiltering(object):
    """Test filtering, querying, and sorting record set results"""

    def test_sorting(self):
        '''Test that records are sorted by designated sort fields
        '''
        pass

    def test_filtering(self):
        '''Test filtering records to include only records with an
        exact match in a field value
        '''
        pass

    def test_querying(self):
        '''Test querying records to include records that match a given
        query or expression
        '''
        pass


class TestAPI(unittest.TestCase):
    """Test the Shorthand API for working with record sets
    embedded within notes
    """

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def test_list_record_sets(self):
        '''Test listing all record sets within notes
        '''
        sets_found = _get_record_sets(CONFIG['notes_directory'],
                                      directory_filter=None,
                                      grep_path=CONFIG['grep_path'])
        all_sets = [{'display_path': 'rec.note',
                     'file_path': '/rec.note',
                     'line_number': '4'}]

        assert sets_found == all_sets

    def test_get_record_set(self):
        '''Test getting the contents of an individual record set
        '''
        loaded_record_set = _get_record_set(CONFIG['notes_directory'],
                                            file_path='/rec.note',
                                            line_number=4,
                                            parse=True,
                                            parse_format='json',
                                            include_config=False)
        loaded_record_set = json.loads(loaded_record_set)

        assert len(loaded_record_set) == 3
