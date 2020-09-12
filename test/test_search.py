import os
import logging
import unittest

from shorthand.utils.logging import setup_logging
from shorthand.search_tools import search_notes, filename_search

from utils import setup_environment
from results_unstamped import EMPTY_RESULTS, SEARCH_RESULTS_FOOD, \
                              SEARCH_RESULTS_FOOD_SENSITIVE, \
                              SEARCH_RESULTS_BALANCED_DIET, ALL_FILES


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


# Define helpers to make the rest of the code cleaner
def get_search_results(query_string, case_sensitive):
    return search_notes(
                notes_directory=CONFIG['notes_directory'],
                query_string=query_string,
                case_sensitive=case_sensitive,
                grep_path=CONFIG['grep_path'])


def get_file_search_results(prefer_recent, query_string, case_sensitive):
    return filename_search(
                notes_directory=CONFIG['notes_directory'],
                prefer_recent_files=prefer_recent,
                cache_directory=CONFIG['cache_directory'],
                query_string=query_string, case_sensitive=case_sensitive,
                grep_path=CONFIG['grep_path'])


class TestSearch(unittest.TestCase):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_search(self):
        '''Test full-text search
        '''

        # Test single keyword search
        search_results = get_search_results('Food', False)
        assert search_results['count'] == SEARCH_RESULTS_FOOD['count']
        self.assertCountEqual(search_results, SEARCH_RESULTS_FOOD)

        # Test case-sensitive single keyword search
        search_results = get_search_results('Food', True)
        assert search_results['count'] == SEARCH_RESULTS_FOOD_SENSITIVE['count']
        self.assertCountEqual(search_results, SEARCH_RESULTS_FOOD_SENSITIVE)

        # Test quoted expression search
        search_results = get_search_results('"balanced diet"', False)
        assert search_results['count'] == SEARCH_RESULTS_BALANCED_DIET['count']
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)

        # Test case-sensitive quoted expression search
        search_results = get_search_results('"balanced diet"', True)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results('"essential part"', True)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results('"Balanced diet"', True)
        self.assertCountEqual(search_results, EMPTY_RESULTS)
        search_results = get_search_results('"essential Part"', True)
        self.assertCountEqual(search_results, EMPTY_RESULTS)

        # Test combination
        search_results = get_search_results('"balanced diet" food', False)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results('"essential part" food', False)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results(
            '"essential part" "balanced diet"', False)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results(
            '"essential part" "balanced diet" food', False)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)

        # Test case-sensitive combination
        search_results = get_search_results('"balanced diet" Food', True)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results('"balanced Diet" food', True)
        self.assertCountEqual(search_results, EMPTY_RESULTS)
        search_results = get_search_results('"essential part" Food', True)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results('"essential part" food', True)
        self.assertCountEqual(search_results, EMPTY_RESULTS)
        search_results = get_search_results(
            '"essential part" "balanced diet"', True)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results(
            '"essential pArt" "balanced diet"', True)
        self.assertCountEqual(search_results, EMPTY_RESULTS)
        search_results = get_search_results(
            '"essential part" "balanced diet" Food', True)
        self.assertCountEqual(search_results, SEARCH_RESULTS_BALANCED_DIET)
        search_results = get_search_results(
            '"essential part" "balanced diet" food', True)
        self.assertCountEqual(search_results, EMPTY_RESULTS)

        # TODO- Test directory filter

    def test_find_file(self):
        '''Test finding notes files
        '''
        all_files_found = get_file_search_results(prefer_recent=True,
                                                  query_string=None,
                                                  case_sensitive=False)
        assert all_files_found == ALL_FILES
