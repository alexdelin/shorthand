import json
import logging

from shorthand.utils.config import clean_and_validate_config

from utils import ShorthandTestCase, LOG_PATH


log = logging.getLogger(__name__)


class TestAPIBasic(ShorthandTestCase, reset_per_method=False, include_flask_client=True):
    """Test basic functionality of the API"""

    def test_status(self):
        response = self.api_client.get('/api/v1/config')
        loaded_response = json.loads(response.data)
        assert isinstance(loaded_response, dict)
        assert 'notes_directory' in loaded_response.keys()
        assert loaded_response == clean_and_validate_config(self.config)

    def test_logging(self):
        response = self.api_client.get('/api/v1/config')
        assert response.data

        # Check that the log file was written to
        with open(LOG_PATH, 'r') as f:
            log_content = f.read()
        assert 'Returning config' in log_content
