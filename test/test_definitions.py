import logging

from utils import ShorthandTestCase
from results_unstamped import ALL_DEFINITIONS


log = logging.getLogger(__name__)


class TestDefinitions(ShorthandTestCase, reset_per_method=False):
    """Test basic search functionality of the library"""

    def test_get_definitions(self):

        definitions = self.server.get_definitions()
        assert len(ALL_DEFINITIONS) == len(definitions)
        self.assertCountEqual(definitions, ALL_DEFINITIONS)
