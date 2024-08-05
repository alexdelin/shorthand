import logging
import unittest

from shorthand.tags import _get_tags, extract_tags

from utils import setup_environment, validate_setup


log = logging.getLogger(__name__)


class TestTags(unittest.TestCase):
    """Test basic search functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.cache_dir = cls.config['cache_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_tags(self):
        all_tags = ['baking', 'bar', 'baz', 'foo', 'food', 'future', 'nested',
                    'philosophy', 'pointless', 'software', 'topic']
        tags_found = set(_get_tags(self.notes_dir,
                                   grep_path=self.grep_path))
        assert tags_found == set(all_tags)

    def test_extract_tags(self):
        input_text = 'This is some text with tags :first: :second: :third:'
        tags, clean_text = extract_tags(input_text)
        assert set(tags) == set(['first', 'second', 'third'])
        assert clean_text == 'This is some text with tags'
