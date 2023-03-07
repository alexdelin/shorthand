import logging
import unittest

from shorthand.history import _get_calendar

from utils import setup_environment, validate_setup, setup_logging
from results_unstamped import CALENDAR


CONFIG = setup_environment()
log = logging.getLogger(__name__)


class TestCalendar(unittest.TestCase):
    """Test Calendar functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_calendar(self):
        calendar = _get_calendar(
            CONFIG['notes_directory'],
            directory_filter=None,
            grep_path=CONFIG['grep_path'])
        assert calendar == CALENDAR
