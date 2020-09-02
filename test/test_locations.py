import os
import logging
import unittest

from shorthand.gps_tools import get_locations
from shorthand.utils.logging import setup_logging

from utils import setup_environment


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestLocations(unittest.TestCase):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_tags(self):
        all_locations = [
            {'latitude': '40.757898', 'longitude': '-73.985502', 'name': 'Times Square', 'file_path': '/locations.note', 'display_path': 'locations.note', 'line_number': '4'},
            {'latitude': '29.978938', 'longitude': '31.134116', 'name': 'The Great Pyramid', 'file_path': '/locations.note', 'display_path': 'locations.note', 'line_number': '5'},
            {'latitude': '36.193521', 'longitude': '-112.048667', 'name': 'The Grand Canyon', 'file_path': '/locations.note', 'display_path': 'locations.note', 'line_number': '6'},
            {'latitude': '48.858212', 'longitude': '2.294513', 'name': '', 'file_path': '/locations.note', 'display_path': 'locations.note', 'line_number': '7'}
        ]
        # Compare returned items ignoring the order
        self.assertCountEqual(get_locations(CONFIG['notes_directory']), all_locations)
