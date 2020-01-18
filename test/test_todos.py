import os
from datetime import datetime

from shorthand.todo_tools import get_todos, stamp_notes

from utils import setup_environment
from model import NoteparserModel


CONFIG = setup_environment()
MODEL = NoteparserModel()


# Helper to make the tests simpler
def get_todo_results(todo_status='incomplete', directory_filter=None, query_string=None,
                     sort_by=None, suppress_future=False, stamp=False):
    return get_todos(notes_directory=CONFIG['notes_directory'],
                     todo_status=todo_status, directory_filter=directory_filter,
                     query_string=query_string, sort_by=sort_by,
                     suppress_future=suppress_future)


class TestUnstampedTodos(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_unstamped_incomplete_todos_basic(self):

        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete'
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section'
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test
            }
            assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date'
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

    def test_unstamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped'
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

    def test_unstamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete'
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)


class TestTodoStamping(object):
    """Test stamping functionality of the library"""

    def test_stamp(self):
        response = stamp_notes(CONFIG['notes_directory'])
        assert response == 'Done!'

    def test_today_replacement(self):
        # Have a list of lines in specific files to check
        # that the placeholder text has been replaced as expected
        pass


class TestStampedTodos(object):
    """Repeat all tests for unstamped todos to ensure that
       nothing unexpected has changed.
    """

    def test_stamped_incomplete_todos_basic(self):
        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete',
            'stamp': True
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section',
            'stamp': True
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test,
                'stamp': True
            }
            assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date',
            'stamp': True
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True,
            'stamp': True
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

    def test_stamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped',
            'stamp': True
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)

    def test_stamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete',
            'stamp': True
        }
        assert get_todo_results(**args) == MODEL.search_todos(**args)
