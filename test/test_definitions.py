import logging
import unittest

from shorthand.elements.definitions import _get_definitions

from utils import setup_environment, validate_setup, setup_logging
from results_unstamped import ALL_DEFINITIONS


CONFIG = setup_environment()
log = logging.getLogger(__name__)


class TestDefinitions(unittest.TestCase):
    """Test basic search functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_definitions(self):

        definitions = _get_definitions(
                        CONFIG['notes_directory'],
                        directory_filter=None,
                        grep_path=CONFIG['grep_path'])
        assert len(ALL_DEFINITIONS) == len(definitions)
        self.assertCountEqual(definitions, ALL_DEFINITIONS)
