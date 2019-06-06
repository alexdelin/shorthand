import os

from note_parser.search_tools import search_notes, get_context

from utils import setup_environment
from results_unstamped import EMPTY_RESULTS, SEARCH_RESULTS_FOOD, \
                              SEARCH_RESULTS_FOOD_SENSITIVE


CONFIG = setup_environment()


# Define helper to make the rest of the code cleaner
def get_search_results(query_string, case_sensitive):
    return search_notes(
                notes_directory=CONFIG['notes_directory'],
                query_string=query_string,
                case_sensitive=case_sensitive)


class TestSearch(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_search(self):

        # Test single keyword search
        query_string = 'food'
        case_sensitive = False
        search_results = get_search_results(query_string, case_sensitive)
        assert search_results == SEARCH_RESULTS_FOOD

        # Test case-sensitive single keyword search
        query_string = 'Food'
        case_sensitive = True
        search_results = get_search_results(query_string, case_sensitive)
        assert search_results == SEARCH_RESULTS_FOOD_SENSITIVE

        # Test quoted expression search
        # Test case-sensitive quoted expression search
        # Test combination
        # Test case-sensitive combination
        # Test directory filter
