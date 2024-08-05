import logging
import unittest

from shorthand.calendar import _get_calendar

from utils import setup_environment, validate_setup, setup_logging
from results_unstamped import CALENDAR


log = logging.getLogger(__name__)


class TestCalendar(unittest.TestCase):
    """Test Calendar functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.cache_dir = cls.config['cache_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_calendar(self):
        calendar = _get_calendar(
            self.notes_dir,
            directory_filter=None,
            grep_path=self.grep_path)
        assert calendar == CALENDAR
