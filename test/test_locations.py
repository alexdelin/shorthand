import os
import logging
import unittest

from shorthand.elements.locations import _get_locations
from shorthand.utils.logging import setup_logging

from utils import setup_environment, validate_setup
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

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_locations(self):
        # Compare returned items ignoring the order
        self.assertCountEqual(fetch_locations(), ALL_LOCATIONS)
