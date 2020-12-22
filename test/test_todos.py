import json
import logging
import unittest

from shorthand.utils.logging import setup_logging
from shorthand.elements.todos import _get_todos
from shorthand.stamping import _stamp_notes
from shorthand.web.app import create_app

from utils import setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH
from model import ShorthandModel


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)
MODEL = ShorthandModel()


# Helper to make the tests simpler
def get_todo_results(todo_status='incomplete', directory_filter=None,
                     query_string=None, sort_by=None, suppress_future=False,
                     stamp=False):
    return _get_todos(notes_directory=CONFIG['notes_directory'],
                      todo_status=todo_status,
                      directory_filter=directory_filter,
                      query_string=query_string, sort_by=sort_by,
                      suppress_future=suppress_future,
                      grep_path=CONFIG['grep_path'])


class TestUnstampedTodos(unittest.TestCase):
    """Test basic search functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_unstamped_incomplete_todos_basic(self):

        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete'
        }
        library_results = get_todo_results(**args)
        model_results = MODEL.search_todos(**args)
        assert set(library_results[0].keys()) == set(model_results[0].keys())
        assert len(library_results) == len(model_results)
        self.assertCountEqual(library_results, model_results)

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section'
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test
            }
            self.assertCountEqual(get_todo_results(**args),
                                  MODEL.search_todos(**args))

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date'
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_unstamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped'
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_unstamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete'
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))


class TestStampedTodos(unittest.TestCase):
    """Repeat all tests for unstamped todos to ensure that
       nothing unexpected has changed.
    """

    @classmethod
    def setup_class(cls):
        '''ensure that we have a clean environment
        before running any tests
        '''
        _ = setup_environment()
        _ = _stamp_notes(CONFIG['notes_directory'],
                         stamp_todos=True, stamp_today=True,
                         stamp_questions=False, stamp_answers=False,
                         grep_path=CONFIG['grep_path'])

    @classmethod
    def teardown_class(cls):
        '''Ensure that we don't leave stamped
        notes around after the tests are run
        '''
        teardown_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_stamped_incomplete_todos_basic(self):
        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete',
            'stamp': True
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test,
                'stamp': True
            }
            self.assertCountEqual(get_todo_results(**args),
                                  MODEL.search_todos(**args))

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date',
            'stamp': True
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True,
            'stamp': True
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_stamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped',
            'stamp': True
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_stamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete',
            'stamp': True
        }
        self.assertCountEqual(get_todo_results(**args),
                              MODEL.search_todos(**args))


class TestTodosUnstampedFlask(unittest.TestCase):
    """Test getting unstamped todos via the HTTP API"""

    maxDiff = None

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()
        app = create_app(TEST_CONFIG_PATH)
        cls.api_client = app.test_client()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def get_api_results(self, todo_status='incomplete', directory_filter=None,
                        query_string=None, sort_by=None, suppress_future=False,
                        stamp=False):
        params = {
            'status': todo_status,
            'directory_filter': directory_filter,
            'query_string': query_string,
            'sort_by': sort_by
        }
        response = self.api_client.get('/api/v1/todos', query_string=params)
        return json.loads(response.data)['items']

    def test_unstamped_incomplete_todos_basic(self):

        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True
        }
        library_results = self.get_api_results(**args)
        model_results = MODEL.search_todos(**args)
        assert set(library_results[0].keys()) == set(model_results[0].keys())
        assert len(library_results) == len(model_results)
        self.assertCountEqual(library_results, model_results)

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section',
            'suppress_future': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test,
                'suppress_future': True
            }
            self.assertCountEqual(self.get_api_results(**args),
                                  MODEL.search_todos(**args))

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date',
            'suppress_future': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

    def test_unstamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped'
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

    def test_unstamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete'
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))
