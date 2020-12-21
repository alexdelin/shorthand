import json
import unittest

from shorthand.web.app import app
from shorthand.utils.config import clean_and_validate_config

from utils import setup_environment, validate_setup, TEST_CONFIG_PATH


CONFIG = setup_environment()


class TestAPIBasic(unittest.TestCase):
    """Test basic functionality of the API"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()
        app.config['config_path'] = TEST_CONFIG_PATH
        cls.api_client = app.test_client()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_status(self):
        response = self.api_client.get('/api/v1/config')
        loaded_response = json.loads(response.data)
        assert isinstance(loaded_response, dict)
        assert 'notes_directory' in loaded_response.keys()
        assert loaded_response == clean_and_validate_config(CONFIG)
