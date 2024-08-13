import logging

from shorthand.tags import extract_tags

from utils import ShorthandTestCase


log = logging.getLogger(__name__)


class TestTags(ShorthandTestCase, reset_per_method=False):
    """Test basic search functionality of the library"""

    def test_get_tags(self):
        all_tags = ['baking', 'bar', 'baz', 'foo', 'food', 'future', 'nested',
                    'philosophy', 'pointless', 'software', 'topic']
        tags_found = set(self.server.get_tags())
        assert tags_found == set(all_tags)

    def test_extract_tags(self):
        input_text = 'This is some text with tags :first: :second: :third:'
        tags, clean_text = extract_tags(input_text)
        assert set(tags) == set(['first', 'second', 'third'])
        assert clean_text == 'This is some text with tags'
