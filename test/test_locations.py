import os
import logging
import unittest

from shorthand.elements.locations import _get_locations
from shorthand.utils.logging import setup_logging

from utils import setup_environment
from results_unstamped import ALL_LOCATIONS


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


# Helper function to make test code cleaner
def fetch_locations(directory_filter=None):
    return _get_locations(CONFIG['notes_directory'],
                          directory_filter=directory_filter,
                          grep_path=CONFIG['grep_path'])


class TestLocations(unittest.TestCase):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_tags(self):
        # Compare returned items ignoring the order
        self.assertCountEqual(fetch_locations(), ALL_LOCATIONS)
