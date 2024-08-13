import logging

from shorthand.toc import _get_toc

from utils import ShorthandTestCase
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


class TestToc(ShorthandTestCase, reset_per_method=False):
    """Test table of contents functionality of the library"""

    def test_get_toc(self):
        toc = _get_toc(self.notes_dir)

        compare_dicts(toc, TOC)
