import os
import logging
import unittest

from shorthand.definition_tools import get_definitions
from shorthand.utils.logging import setup_logging

from utils import setup_environment


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestDefinitions(unittest.TestCase):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_definitions(self):

        all_definitions = [
            {'definition': 'A formal meaning attached to a specific term','display_path': 'definitions.note','file_path': '/definitions.note','line_number': '5','term': 'definition'},
            {'definition': 'A tool you can use to make your life easier and better','display_path': 'definitions.note','file_path': '/definitions.note','line_number': '6','term': 'software'},
            {'definition': 'Something that you eat when you are hungry','display_path': 'definitions.note','file_path': '/definitions.note','line_number': '7','term': 'food'},
            {'definition': 'The flaky part at the bottom of the pie :baking:','display_path': 'section → mixed.note','file_path': '/section/mixed.note','line_number': '9','term': 'crust'}
        ]
        definitions = get_definitions(
                        CONFIG['notes_directory'],
                        directory_filter=None,
                        grep_path=CONFIG['grep_path'])
        assert len(all_definitions) == len(definitions)
        self.assertCountEqual(definitions, all_definitions)
