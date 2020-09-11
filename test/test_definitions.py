import os
import logging
import unittest

from shorthand.definition_tools import get_definitions
from shorthand.utils.logging import setup_logging

from utils import setup_environment
from results_unstamped import ALL_DEFINITIONS


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestDefinitions(unittest.TestCase):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_definitions(self):

        definitions = get_definitions(
                        CONFIG['notes_directory'],
                        directory_filter=None,
                        grep_path=CONFIG['grep_path'])
        assert len(ALL_DEFINITIONS) == len(definitions)
        self.assertCountEqual(definitions, ALL_DEFINITIONS)
