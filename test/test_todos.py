import json
import logging
import random
import unittest

from shorthand.elements.todos import _get_todos, _mark_todo
from shorthand.stamping import _stamp_notes
from shorthand.web.app import create_app

from utils import setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH, setup_logging
from model import ShorthandModel


CONFIG = setup_environment()
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


class TestMarkTodos(unittest.TestCase):
    """Test Marking the status of a todo
    """

    @classmethod
    def setup_class(cls):
        '''ensure that we have a clean environment
        before running any tests
        '''
        _ = setup_environment()

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

    def test_mark_todo(self):
        # Mark a specific todo as completed
        _mark_todo(notes_directory=CONFIG['notes_directory'],
                   note_path='/todos.note', line_number=6, status='complete')

        # Get all completed todos
        results = get_todo_results(todo_status='complete')

        # Check that the todo we modified now appears completed
        assert any(['Something to do' in todo['todo_text']
                    for todo in results])

        # Mark a specific todo as skipped
        _mark_todo(notes_directory=CONFIG['notes_directory'],
                   note_path='/todos.note', line_number=6, status='skipped')

        # Get all skipped todos
        results = get_todo_results(todo_status='skipped')

        # Check that the todo we modified now appears skipped
        assert any(['Something to do' in todo['todo_text']
                    for todo in results])


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

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()
        app = create_app(TEST_CONFIG_PATH)
        cls.api_client = app.test_client()

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

    def get_api_results(self, todo_status='incomplete', directory_filter=None,
                        query_string=None, case_sensitive=False, sort_by=None,
                        suppress_future=False, stamp=False, tag=None):
        params = {
            'status': todo_status,
            'directory_filter': directory_filter,
            'query_string': query_string,
            'case_sensitive': case_sensitive,
            'sort_by': sort_by,
            'suppress_future': suppress_future,
            'tag': tag
        }
        response_json = self.api_client.get('/api/v1/todos', query_string=params)
        response = json.loads(response_json.data)
        if response.get('error'):
            raise ValueError(f'Got server Error: {response["error"]}')
        else:
            return response['items']

    def test_unstamped_incomplete_todos_basic(self):

        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete',
            'suppress_future': False
        }
        library_results = self.get_api_results(**args)
        model_results = MODEL.search_todos(**args)
        assert set(library_results[0].keys()) == set(model_results[0].keys())
        assert len(library_results) == len(model_results)
        self.assertCountEqual(library_results, model_results)

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section'
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test,
                'case_sensitive': False
            }
            self.assertCountEqual(self.get_api_results(**args),
                                  MODEL.search_todos(**args))

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date'
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

        # Test Tag Filtering
        args = {
            'todo_status': 'incomplete',
            'tag': 'nested'
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

    def test_unstamped_all_combinations(self):
        # Test random combinations of valid properties
        status_options = ['incomplete', 'complete', 'skipped']
        directory_filter_options = [None, 'section']
        query_options = ['cooking', '"follow up"', '"follow up" cooking',
                         'Indented']
        case_sensitive_options = [True, False]
        sort_by_options = [None, 'start_date']
        suppress_future_options = [True, False]
        tag_options = [None, 'future', 'nested', 'pointless', 'topic',
                       'doesntexist']

        for _ in range(50):
            args = {
                'todo_status': random.choice(status_options),
                'directory_filter': random.choice(directory_filter_options),
                'query_string': random.choice(query_options),
                'case_sensitive': random.choice(case_sensitive_options),
                'sort_by': random.choice(sort_by_options),
                'suppress_future': random.choice(suppress_future_options),
                'tag': random.choice(tag_options)
            }
            self.assertCountEqual(self.get_api_results(**args),
                                  MODEL.search_todos(**args))


class TestTodosStampedFlask(unittest.TestCase):
    """Test getting stamped todos via the HTTP API"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()
        _ = _stamp_notes(CONFIG['notes_directory'],
                         stamp_todos=True, stamp_today=True,
                         stamp_questions=False, stamp_answers=False,
                         grep_path=CONFIG['grep_path'])
        app = create_app(TEST_CONFIG_PATH)
        cls.api_client = app.test_client()

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

    def get_api_results(self, todo_status='incomplete', directory_filter=None,
                        query_string=None, case_sensitive=False, sort_by=None,
                        suppress_future=False, stamp=False, tag=None):
        params = {
            'status': todo_status,
            'directory_filter': directory_filter,
            'query_string': query_string,
            'case_sensitive': case_sensitive,
            'sort_by': sort_by,
            'suppress_future': suppress_future,
            'tag': tag
        }
        json_response = self.api_client.get('/api/v1/todos', query_string=params)
        response = json.loads(json_response.data)
        if response.get('error'):
            raise ValueError(f'Got server Error: {response["error"]}')
        else:
            return response['items']


    def test_stamped_incomplete_todos_basic(self):
        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete',
            'stamp': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test,
                'stamp': True
            }
            self.assertCountEqual(self.get_api_results(**args),
                                  MODEL.search_todos(**args))

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date',
            'stamp': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True,
            'stamp': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

    def test_stamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped',
            'stamp': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

    def test_stamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete',
            'stamp': True
        }
        self.assertCountEqual(self.get_api_results(**args),
                              MODEL.search_todos(**args))

    def test_stamped_all_combinations(self):
        # Test random combinations of valid properties
        status_options = ['incomplete', 'complete', 'skipped']
        directory_filter_options = [None, 'section']
        query_options = ['cooking', '"follow up"', '"follow up" cooking',
                         'Indented']
        case_sensitive_options = [True, False]
        sort_by_options = [None, 'start_date']
        suppress_future_options = [True, False]
        tag_options = [None, 'future', 'nested', 'pointless', 'topic',
                       'doesntexist']

        for _ in range(50):
            args = {
                'todo_status': random.choice(status_options),
                'directory_filter': random.choice(directory_filter_options),
                'query_string': random.choice(query_options),
                'case_sensitive': random.choice(case_sensitive_options),
                'sort_by': random.choice(sort_by_options),
                'suppress_future': random.choice(suppress_future_options),
                'tag': random.choice(tag_options),
                'stamp': True
            }
            self.assertCountEqual(self.get_api_results(**args),
                                  MODEL.search_todos(**args))


class TestMarkTodosFlask(unittest.TestCase):
    """Test Marking the status of a todo via the HTTP API
    """

    @classmethod
    def setup_class(cls):
        '''ensure that we have a clean environment
        before running any tests
        '''
        _ = setup_environment()
        app = create_app(TEST_CONFIG_PATH)
        cls.api_client = app.test_client()

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

    def test_mark_todo(self):
        # Mark a specific todo as completed
        params = {
            'filename': '/todos.note',
            'line_number': 6,
            'status': 'complete'
        }
        self.api_client.post('/api/v1/mark_todo', query_string=params)

        # Get all completed todos
        params = {'status': 'complete'}
        results = self.api_client.get('/api/v1/todos', query_string=params)
        results = json.loads(results.data)['items']

        # Check that the todo we modified now appears completed
        assert any(['Something to do' in todo['todo_text']
                    for todo in results])

        # Mark a specific todo as skipped
        params = {
            'filename': '/todos.note',
            'line_number': 6,
            'status': 'skipped'
        }
        self.api_client.post('/api/v1/mark_todo', query_string=params)

        # Get all skipped todos
        params = {'status': 'skipped'}
        results = self.api_client.get('/api/v1/todos', query_string=params)
        results = json.loads(results.data)['items']

        # Check that the todo we modified now appears skipped
        assert any(['Something to do' in todo['todo_text']
                    for todo in results])
