import logging
import unittest

from shorthand.toc import _get_toc

from utils import setup_environment, validate_setup, setup_logging
from results_unstamped import TOC


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestToc(unittest.TestCase):
    """Test table of contents functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_toc(self):
        toc = _get_toc(CONFIG['notes_directory'], directory_filter=None)
        assert toc == TOC
