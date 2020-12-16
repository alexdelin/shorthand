import os
import logging
import unittest

from shorthand.utils.logging import setup_logging
from shorthand.search import _search_notes, _filename_search, \
                             _record_file_view
from shorthand.frontend.typeahead import update_ngram_database, \
                                         _get_typeahead_suggestions

from utils import setup_environment, validate_setup
from results_unstamped import EMPTY_RESULTS, SEARCH_RESULTS_FOOD, \
                              SEARCH_RESULTS_FOOD_SENSITIVE, \
                              SEARCH_RESULTS_BALANCED_DIET, ALL_FILES


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


# Define helpers to make the rest of the code cleaner
def get_search_results(query_string, case_sensitive):
    return _search_notes(
                notes_directory=CONFIG['notes_directory'],
                query_string=query_string,
                case_sensitive=case_sensitive,
                grep_path=CONFIG['grep_path'])


def get_file_search_results(prefer_recent, query_string, case_sensitive):
    return _filename_search(
                notes_directory=CONFIG['notes_directory'],
                prefer_recent_files=prefer_recent,
                cache_directory=CONFIG['cache_directory'],
                query_string=query_string, case_sensitive=case_sensitive,
                grep_path=CONFIG['grep_path'])


def get_typeahead_results(string):
    return _get_typeahead_suggestions(CONFIG['cache_directory'], string)


class TestSearch(unittest.TestCase):
    """Test basic search functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

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


class TestFileFinder(unittest.TestCase):

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def search_helper(self, query_string, case_sensitive=False):
        '''A sort-of model to test the implementation against
        '''
        all_files_found = ALL_FILES
        if not case_sensitive:
            query_string = query_string.lower()
            all_files_found = [file.lower() for file in all_files_found]

        return [file
                for file in all_files_found
                if all([query_component in file
                        for query_component in query_string.split(' ')])
                ]

    def test_find_all_files(self):
        '''Test finding all notes files
        '''
        all_files_found = get_file_search_results(prefer_recent=True,
                                                  query_string=None,
                                                  case_sensitive=False)
        assert set(all_files_found) == set(ALL_FILES)

    def test_file_search(self):
        '''Test searching for files via substrings (non case sensitive)
        '''

        test_queries = [
            'foo',  # Should have no results
            'note',  # Matches Everything
            'foo note',  # Matches Everything
            'todos',  # Should have one result
            'section mix',  # Query string with multiple components
            'sample'  # Part of the parent dirname
        ]
        for query_string in test_queries:
            expected_results = self.search_helper(query_string,
                                                  case_sensitive=False)
            real_results = get_file_search_results(prefer_recent=False,
                                                   query_string=query_string,
                                                   case_sensitive=False)
            assert set(expected_results) == set(real_results)

    def test_file_search_case_sensitive(self):
        '''Test searching for files via substrings (case sensitive)
        '''

        test_queries = [
            'foo',  # Should have no results
            'note',  # Matches Everything
            'todos',  # Should have one result
            'Todos',  # Should have no results
            'section mix',  # Query string with multiple components
            'section Mix',  # no results
            'sample'  # Part of the parent dirname
        ]
        for query_string in test_queries:
            expected_results = self.search_helper(query_string,
                                                  case_sensitive=True)
            real_results = get_file_search_results(prefer_recent=False,
                                                   query_string=query_string,
                                                   case_sensitive=True)
            assert set(expected_results) == set(real_results)

    def test_recent_file_preference(self):
        '''Test that the implementation prefers recently accessed files
        '''

        # Test that the history file starts off not existing
        history_file = CONFIG['cache_directory'] + '/recent_files.txt'
        assert not os.path.exists(history_file)

        # Verify that most recent views get bumped to the top
        for _ in range(5):
            # View the last file returned
            all_files_found = get_file_search_results(prefer_recent=True,
                                                      query_string=None,
                                                      case_sensitive=False)
            last_file = all_files_found[-1]
            _record_file_view(CONFIG['cache_directory'],
                              last_file, history_limit=100)

            # Verify that the view was recorded in the history file
            assert os.path.exists(history_file)
            with open(history_file, 'r') as history_file_object:
                history_data = history_file_object.read()
            assert len(history_data) > 0
            assert last_file in history_data

            # Verify that the viewed file now shows up first
            file_search_results = get_file_search_results(prefer_recent=True,
                                                          query_string='note',
                                                          case_sensitive=False)
            assert file_search_results[0] == last_file


class TestTypeahead(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()
        _ = update_ngram_database(CONFIG['notes_directory'],
                                  CONFIG['cache_directory'])

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_typeahead_unigram(self):

        results = get_typeahead_results('foo')
        assert results == ['food']

        results = get_typeahead_results('inc')
        assert results == ['includes', 'inclues', 'included', 'incomplete']

    def test_typeahead_bigram(self):

        results = get_typeahead_results('"apple p')
        assert results == ['"apple pie"']

        results = get_typeahead_results('"for t')
        assert results == ['"for this"', '"for the"']

    def test_typeahead_trigram(self):

        results = get_typeahead_results('"what is t')
        assert results == ['"what is the"']

    def test_typeahead_invalid(self):

        results = get_typeahead_results('"the best apple p')
        assert results == []
