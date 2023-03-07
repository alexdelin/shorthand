import json
import logging
import unittest

from shorthand.web.app import create_app
from shorthand.utils.config import clean_and_validate_config

from utils import setup_environment, validate_setup, TEST_CONFIG_PATH, \
                  LOG_PATH, setup_logging


CONFIG = setup_environment()
log = logging.getLogger(__name__)


class TestAPIBasic(unittest.TestCase):
    """Test basic functionality of the API"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()
        app = create_app(TEST_CONFIG_PATH)
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

    def test_logging(self):
        response = self.api_client.get('/api/v1/config')
        assert response.data

        # Check that the log file was written to
        with open(LOG_PATH, 'r') as f:
            log_content = f.read()
        assert 'Returning config' in log_content
