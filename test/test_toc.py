import logging
import unittest

from shorthand.toc import _get_toc

from utils import setup_environment, validate_setup
from results_unstamped import TOC


log = logging.getLogger(__name__)


def compare_dicts(d1, d2):
    assert set(d1.keys()) == set(d2.keys())
    for key, value in d1.items():
        if isinstance(value, str):
            assert d1[key] == d2[key]
        elif isinstance(value, list):
            assert len(d1[key]) == len(d2[key])
            if len(value) > 0:
                if isinstance(value[0], str):
                    assert set(d1[key]) == set(d2[key])
                elif isinstance(value[0], dict):
                    for i in range(len(d1[key])):
                        compare_dicts(d1[key][i], d2[key][i])
            else:
                assert d1[key] == d2[key]


class TestToc(unittest.TestCase):
    """Test table of contents functionality of the library"""

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

    def test_get_toc(self):
        toc = _get_toc(self.notes_dir)

        compare_dicts(toc, TOC)
