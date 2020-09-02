import os
import logging
import unittest

from shorthand.utils.logging import setup_logging

from utils import setup_environment


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestDefinitions(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_definitions(self):
        pass
