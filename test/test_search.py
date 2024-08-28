import os
import nltk
import logging

from shorthand.search import _search_full_text, _search_filenames, \
                             _record_file_view
from shorthand.frontend.typeahead import _get_typeahead_suggestions, _update_ngram_database

from utils import ShorthandTestCase, setup_environment
from results_unstamped import SEARCH_RESULTS_FOOD, \
                              SEARCH_RESULTS_FOOD_SENSITIVE, \
                              SEARCH_RESULTS_BALANCED_DIET, ALL_FILES


log = logging.getLogger(__name__)


class TestSearch(ShorthandTestCase, reset_per_method=False):
    """Test basic search functionality of the library"""

    def get_search_results(self, query_string, case_sensitive):
        return _search_full_text(
                    notes_directory=self.notes_dir,
                    query_string=query_string,
                    case_sensitive=case_sensitive,
                    grep_path=self.grep_path)

    def test_search(self):
        '''Test full-text search
        '''

        # Test single keyword search
        search_results = self.get_search_results('Food', False)
        assert len(search_results) == len(SEARCH_RESULTS_FOOD)
        assert search_results == SEARCH_RESULTS_FOOD

        # Test case-sensitive single keyword search
        search_results = self.get_search_results('Food', True)
        assert len(search_results) == len(SEARCH_RESULTS_FOOD_SENSITIVE)
        assert search_results == SEARCH_RESULTS_FOOD_SENSITIVE

        # Test quoted expression search
        search_results = self.get_search_results('"balanced diet"', False)
        assert len(search_results) == len(SEARCH_RESULTS_BALANCED_DIET)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET

        # Test case-sensitive quoted expression search
        search_results = self.get_search_results('"balanced diet"', True)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results('"essential part"', True)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results('"Balanced diet"', True)
        assert search_results == []
        search_results = self.get_search_results('"essential Part"', True)
        assert search_results == []

        # Test combination
        search_results = self.get_search_results('"balanced diet" food', False)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results('"essential part" food', False)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results(
            '"essential part" "balanced diet"', False)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results(
            '"essential part" "balanced diet" food', False)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET

        # Test case-sensitive combination
        search_results = self.get_search_results('"balanced diet" Food', True)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results('"balanced Diet" food', True)
        assert search_results == []
        search_results = self.get_search_results('"essential part" Food', True)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results('"essential part" food', True)
        assert search_results == []
        search_results = self.get_search_results(
            '"essential part" "balanced diet"', True)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results(
            '"essential pArt" "balanced diet"', True)
        assert search_results == []
        search_results = self.get_search_results(
            '"essential part" "balanced diet" Food', True)
        assert search_results == SEARCH_RESULTS_BALANCED_DIET
        search_results = self.get_search_results(
            '"essential part" "balanced diet" food', True)
        assert search_results == []

        # TODO- Test directory filter


class TestFileFinder(ShorthandTestCase, reset_per_method=False):

    def get_file_search_results(self, prefer_recent, query_string, case_sensitive):
        return _search_filenames(
                    notes_directory=self.notes_dir,
                    prefer_recent_files=prefer_recent,
                    query_string=query_string, case_sensitive=case_sensitive,
                    grep_path=self.grep_path)

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
            real_results = self.get_file_search_results(prefer_recent=False,
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
            real_results = self.get_file_search_results(prefer_recent=False,
                                                        query_string=query_string,
                                                        case_sensitive=True)
            assert set(expected_results) == set(real_results)

    def test_recent_file_preference(self):
        '''Test that the implementation prefers recently accessed files
        '''

        # Test that the history file starts off not existing
        history_file = self.notes_dir + '/.shorthand/state/recent_files.txt'
        assert not os.path.exists(history_file)

        # Verify that most recent views get bumped to the top
        for _ in range(5):
            # View the last file returned
            all_files_found = self.get_file_search_results(prefer_recent=True,
                                                           query_string='note',
                                                           case_sensitive=False)
            last_file = all_files_found[-1]
            _record_file_view(self.notes_dir,
                              last_file, history_limit=100)

            # Verify that the view was recorded in the history file
            assert os.path.exists(history_file)
            with open(history_file, 'r') as history_file_object:
                history_data = history_file_object.read()
            assert len(history_data) > 0
            assert last_file in history_data

            # Verify that the viewed file now shows up first
            file_search_results = self.get_file_search_results(prefer_recent=True,
                                                               query_string='note',
                                                               case_sensitive=False)
            assert file_search_results[0] == last_file


class TestTypeahead(ShorthandTestCase, reset_per_method=False):

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']
        nltk.download('punkt_tab')
        _update_ngram_database(cls.notes_dir)

    def get_typeahead_results(self, string):
        return _get_typeahead_suggestions(self.notes_dir, string)

    def test_typeahead_unigram(self):

        results = self.get_typeahead_results('foo')
        assert results == ['food']

        results = self.get_typeahead_results('inc')
        assert set(results) == set(['includes', 'included', 'incomplete'])

    def test_typeahead_bigram(self):

        results = self.get_typeahead_results('"apple p')
        assert results == ['"apple pie"']

        results = self.get_typeahead_results('"for t')
        assert set(results) == set(['"for this"', '"for the"'])

    def test_typeahead_trigram(self):

        results = self.get_typeahead_results('"what is t')
        assert results == ['"what is the"']

    def test_typeahead_invalid(self):

        results = self.get_typeahead_results('"the best apple p')
        assert results == []
