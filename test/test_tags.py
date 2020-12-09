import os
import logging
import unittest

from shorthand.tags import _get_tags, extract_tags
from shorthand.utils.logging import setup_logging

from utils import setup_environment


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestTags(unittest.TestCase):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_tags(self):
        all_tags = ['baking', 'bar', 'baz', 'foo', 'food', 'future', 'nested',
                    'philosophy', 'pointless', 'software', 'topic']
        tags_found = set(_get_tags(CONFIG['notes_directory'],
                                   grep_path=CONFIG['grep_path']))
        assert tags_found == set(all_tags)

    def test_extract_tags(self):
        input_text = 'This is some text with tags :first: :second: :third:'
        tags, clean_text = extract_tags(input_text)
        assert set(tags) == set(['first', 'second', 'third'])
        assert clean_text == 'This is some text with tags'
