import logging

from shorthand.calendar import _get_calendar

from utils import ShorthandTestCase
from results_unstamped import CALENDAR


log = logging.getLogger(__name__)


class TestCalendar(ShorthandTestCase, reset_per_method=False):
    """Test Calendar functionality of the library"""

    def test_get_calendar(self):
        calendar = _get_calendar(
            self.notes_dir,
            directory_filter=None,
            grep_path=self.grep_path)
        assert calendar == CALENDAR
