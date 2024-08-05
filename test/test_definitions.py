import logging
import unittest

from shorthand.elements.definitions import _get_definitions

from utils import setup_environment, validate_setup
from results_unstamped import ALL_DEFINITIONS


log = logging.getLogger(__name__)


class TestDefinitions(unittest.TestCase):
    """Test basic search functionality of the library"""

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

    def test_get_definitions(self):

        definitions = _get_definitions(
                        self.notes_dir,
                        directory_filter=None,
                        grep_path=self.grep_path)
        assert len(ALL_DEFINITIONS) == len(definitions)
        self.assertCountEqual(definitions, ALL_DEFINITIONS)
