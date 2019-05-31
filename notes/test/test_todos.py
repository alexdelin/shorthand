import os

from note_parser.todo_tools import get_todos, mark_todo, stamp_notes

from utils import setup_environment
from results_unstamped import ALL_INCOMPLETE_TODOS, ALL_SKIPPED_TODOS, \
                              ALL_COMPLETE_TODOS


CONFIG = setup_environment()


class TestTodos(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    # ----- ToDos -----
    def test_get_incomplete_todos(self):
        # Test Getting all incomplete todos
        all_incomplete_todos = get_todos(
                notes_directory=CONFIG['notes_directory'],
                todo_status='incomplete', directory_filter=None,
                query_string=None, sort_by='start_date',
                suppress_future=False)
        assert all_incomplete_todos == ALL_INCOMPLETE_TODOS

        # Test Directory filter
        # Test Query String
        # Test Sort Order
        # Test Suppress Future
        # Test Tag Filter

    def test_skipped_todos(self):
        all_skipped_todos = get_todos(
                notes_directory=CONFIG['notes_directory'],
                todo_status='skipped', directory_filter=None,
                query_string=None, sort_by='start_date',
                suppress_future=False)
        assert all_skipped_todos == ALL_SKIPPED_TODOS

    def test_get_complete_todos(self):
        all_complete_todos = get_todos(
                notes_directory=CONFIG['notes_directory'],
                todo_status='complete', directory_filter=None,
                query_string=None, sort_by='start_date',
                suppress_future=False)
        assert all_complete_todos == ALL_COMPLETE_TODOS

    def test_invalid_todo_request(self):
        pass
