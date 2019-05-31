import os

from note_parser.search_tools import search_notes, get_context

from utils import setup_environment


CONFIG = setup_environment()


class TestSearch(object):
    """Test basic search functionality of the library"""

    def test_setup(self):

        test_dir = CONFIG['notes_directory']
        assert os.path.exists(test_dir)

    def test_search(self):
        pass
