import os

from note_parser.search_tools import search_notes, get_context

from utils import setup_environment
from results_unstamped import SEARCH_RESULTS_FOOD


CONFIG = setup_environment()


class TestSearch(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_search(self):

        # Test single keyword search
        query_string = 'food'
        search_results = search_notes(
                notes_directory=CONFIG['notes_directory'],
                query_string=query_string,
                case_sensitive=False)
        assert search_results == SEARCH_RESULTS_FOOD

        # Test case-sensitive single keyword search
        # Test quoted expression search
        # Test case-sensitive quoted expression search
        # Test combination
        # Test case-sensitive combination
        # Test directory filter
