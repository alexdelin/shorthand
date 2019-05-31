import os

from note_parser.todo_tools import get_todos, mark_todo, stamp_notes

from utils import setup_environment
from results import ALL_INCOMPLETE_TODOS


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

    def test_skipped_todos(self):
        pass

    def test_get_complete_todos(self):
        pass

    def test_invalid_todo_request(self):
        pass
