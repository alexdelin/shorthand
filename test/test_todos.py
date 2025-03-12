import logging

from shorthand.elements.todos import _mark_todo

from utils import ShorthandTestCase
from model import ShorthandModel


log = logging.getLogger(__name__)
MODEL = ShorthandModel()


class TestUnstampedTodos(ShorthandTestCase):
    """Test basic search functionality of the library"""

    def get_todo_results(self, todo_status='incomplete', directory_filter=None,
                         query_string=None, sort_by=None, suppress_future=False,
                         stamp=False):
        return self.server.get_todos(
            todo_status=todo_status,
            directory_filter=directory_filter,
            query_string=query_string, sort_by=sort_by,
            suppress_future=suppress_future)

    def test_unstamped_incomplete_todos_basic(self):

        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete'
        }
        library_results = self.get_todo_results(**args)
        model_results = MODEL.search_todos(**args)
        assert set(library_results[0].keys()) == set(model_results[0].keys())
        assert len(library_results) == len(model_results)
        self.assertCountEqual(library_results, model_results)

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section'
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test
            }
            self.assertCountEqual(self.get_todo_results(**args),
                                  MODEL.search_todos(**args))

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date'
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_unstamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped'
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_unstamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete'
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))


class TestMarkTodos(ShorthandTestCase, reset_per_method=False):
    """Test Marking the status of a todo
    """

    def get_todo_results(self, todo_status='incomplete', directory_filter=None,
                         query_string=None, sort_by=None, suppress_future=False,
                         stamp=False):
        return self.server.get_todos(
            todo_status=todo_status,
            directory_filter=directory_filter,
            query_string=query_string, sort_by=sort_by,
            suppress_future=suppress_future)

    def test_mark_todo(self):
        # Mark a specific todo as completed
        _mark_todo(notes_directory=self.notes_dir,
                   note_path='/todos.note', line_number=6, status='complete')

        # Get all completed todos
        results = self.get_todo_results(todo_status='complete')

        # Check that the todo we modified now appears completed
        assert any(['Something to do' in todo['todo_text']
                    for todo in results])

        # Mark a specific todo as skipped
        _mark_todo(notes_directory=self.notes_dir,
                   note_path='/todos.note', line_number=6, status='skipped')

        # Get all skipped todos
        results = self.get_todo_results(todo_status='skipped')

        # Check that the todo we modified now appears skipped
        assert any(['Something to do' in todo['todo_text']
                    for todo in results])


class TestStampedTodos(ShorthandTestCase, reset_per_method=False, stamp=True):
    """Repeat all tests for unstamped todos to ensure that
       nothing unexpected has changed.
    """

    def get_todo_results(self, todo_status='incomplete', directory_filter=None,
                         query_string=None, sort_by=None, suppress_future=False,
                         stamp=False):
        return self.server.get_todos(
            todo_status=todo_status,
            directory_filter=directory_filter,
            query_string=query_string, sort_by=sort_by,
            suppress_future=suppress_future)

    def test_stamped_incomplete_todos_basic(self):
        # Test Getting all incomplete todos
        args = {
            'todo_status': 'incomplete',
            'stamp': True
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Directory filter
        args = {
            'todo_status': 'incomplete',
            'directory_filter': 'section',
            'stamp': True
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Query String
        query_tests = ['cooking', '"follow up"', '"follow up" cooking']
        for query_test in query_tests:
            args = {
                'todo_status': 'incomplete',
                'query_string': query_test,
                'stamp': True
            }
            self.assertCountEqual(self.get_todo_results(**args),
                                  MODEL.search_todos(**args))

        # Test Sort Order
        args = {
            'todo_status': 'incomplete',
            'sort_by': 'start_date',
            'stamp': True
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

        # Test Suppress Future
        args = {
            'todo_status': 'incomplete',
            'suppress_future': True,
            'stamp': True
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_stamped_skipped_todos_basic(self):
        args = {
            'todo_status': 'skipped',
            'stamp': True
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

    def test_stamped_complete_todos_basic(self):
        args = {
            'todo_status': 'complete',
            'stamp': True
        }
        self.assertCountEqual(self.get_todo_results(**args),
                              MODEL.search_todos(**args))

