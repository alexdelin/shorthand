import os
from datetime import datetime

from note_parser.todo_tools import get_todos, mark_todo, stamp_notes

from utils import setup_environment
from results_unstamped import ALL_INCOMPLETE_TODOS, ALL_SKIPPED_TODOS, \
                              ALL_COMPLETE_TODOS


CONFIG = setup_environment()


# Helper to make the tests simpler
def get_todo_results(todo_status='incomplete', directory_filter=None, query_string=None,
                     sort_by='start_date', suppress_future=False):
    return get_todos(notes_directory=CONFIG['notes_directory'],
                     todo_status=todo_status, directory_filter=directory_filter,
                     query_string=query_string, sort_by=sort_by,
                     suppress_future=suppress_future)


class TestPrestampedTodos(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_incomplete_todos(self):
        # Test Getting all incomplete todos
        all_incomplete_todos = get_todo_results('incomplete')
        assert all_incomplete_todos == ALL_INCOMPLETE_TODOS

        # Test Directory filter
        # Test Query String
        # Test Sort Order
        # Test Suppress Future
        # Test Tag Filter

    def test_skipped_todos(self):
        all_skipped_todos = get_todo_results('skipped')
        assert all_skipped_todos == ALL_SKIPPED_TODOS

    def test_get_complete_todos(self):
        all_complete_todos = get_todo_results('complete')
        assert all_complete_todos == ALL_COMPLETE_TODOS

    def test_invalid_todo_request(self):
        pass


class TestTodoStamping(object):
    """Test stamping functionality of the library"""

    def test_stamp(self):
        response = stamp_notes(CONFIG['notes_directory'])
        assert response == 'Done!'

    def test_today_replacement(self):
        # Have a list of lines in specific files to check
        # that the placeholder text has been replaced as expected
        pass

    def test_todo_date_stamping(self):
        # Get todo content after stamping
        stamped_incomplete_todos = get_todo_results('incomplete')
        stamped_skipped_todos = get_todo_results('skipped')
        stamped_complete_todos = get_todo_results('complete')

        # Check number of items returned
        assert len(stamped_incomplete_todos['items']) == len(ALL_INCOMPLETE_TODOS['items'])
        assert stamped_incomplete_todos['count'] == ALL_INCOMPLETE_TODOS['count']
        assert len(stamped_skipped_todos['items']) == len(ALL_SKIPPED_TODOS['items'])
        assert stamped_skipped_todos['count'] == ALL_SKIPPED_TODOS['count']
        assert len(stamped_complete_todos['items']) == len(ALL_COMPLETE_TODOS['items'])
        assert stamped_complete_todos['count'] == ALL_COMPLETE_TODOS['count']

        # Check that every Incomplete todo has a start date and *not* an end date
        for todo in stamped_incomplete_todos['items']:
            assert todo['start_date']
            assert not todo['end_date']

        # Check that every Skipped todo has both a start date and end date
        for todo in stamped_skipped_todos['items']:
            assert todo['start_date']
            assert todo['end_date']

        # Check that every Complete todo has both a start date and end date
        for todo in stamped_complete_todos['items']:
            assert todo['start_date']
            assert todo['end_date']

        # Check that the contents (other than date) of each todo have
        # not changed due to stamping
        expected_incomplete_results = []
        for todo in ALL_INCOMPLETE_TODOS['items']:
            expected_result = todo
            if not expected_result.get('start_date'):
                expected_result['start_date'] = datetime.now().isoformat()[:10]
            expected_incomplete_results.append(expected_result)
        expected_incomplete_results = sorted(
            expected_incomplete_results, key=lambda k: k['start_date'], reverse=True)
        assert expected_incomplete_results == stamped_incomplete_todos['items']

