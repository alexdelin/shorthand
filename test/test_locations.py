import logging

from shorthand.elements.locations import _get_locations

from utils import ShorthandTestCase
from results_unstamped import ALL_LOCATIONS


log = logging.getLogger(__name__)


class TestLocations(ShorthandTestCase, reset_per_method=False):
    """Test basic search functionality of the library"""

    def fetch_locations(self, directory_filter=None):
        return _get_locations(self.notes_dir,
                              directory_filter=directory_filter,
                              grep_path=self.grep_path)

    def test_get_locations(self):
        # Compare returned items ignoring the order
        self.assertCountEqual(self.fetch_locations(), ALL_LOCATIONS)
