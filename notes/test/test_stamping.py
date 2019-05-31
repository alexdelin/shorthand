import os

from note_parser.todo_tools import get_todos, stamp_notes

from utils import setup_environment
from results_unstamped import ALL_INCOMPLETE_TODOS, ALL_SKIPPED_TODOS, \
                              ALL_COMPLETE_TODOS


CONFIG = setup_environment()


class TestStamping(object):
    """Test stamping functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_stamp(self):
        response = stamp_notes(CONFIG['notes_directory'])

    def test_today_replacement(self):
        pass

    def test_todo_date_stamping(self):
        # Check that every Incomplete todo has a start date
        # Check that every Skipped todo has both a start date and end date
        # Check that every Complete todo has both a start date and end date
        pass
