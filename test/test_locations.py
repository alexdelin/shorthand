import logging
import unittest

from shorthand.elements.locations import _get_locations

from utils import setup_environment, validate_setup, setup_logging
from results_unstamped import ALL_LOCATIONS


log = logging.getLogger(__name__)


class TestLocations(unittest.TestCase):
    """Test basic search functionality of the library"""

    def fetch_locations(self, directory_filter=None):
        return _get_locations(self.notes_dir,
                              directory_filter=directory_filter,
                              grep_path=self.grep_path)

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_locations(self):
        # Compare returned items ignoring the order
        self.assertCountEqual(self.fetch_locations(), ALL_LOCATIONS)
