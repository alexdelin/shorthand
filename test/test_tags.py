import os

from note_parser.tag_tools import get_tags

from utils import setup_environment


CONFIG = setup_environment()


class TestTags(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_get_tags(self):
        pass
