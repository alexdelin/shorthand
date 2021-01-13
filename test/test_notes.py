import json
import logging
import unittest

from shorthand.notes import _get_note, _update_note, _validate_internal_links
from shorthand.utils.logging import setup_logging
from shorthand.web.app import create_app

from utils import setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH


CONFIG = setup_environment()
setup_logging(CONFIG)
log = logging.getLogger(__name__)


class TestNotesOperations(unittest.TestCase):
    """Test basic operations on note files via the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    @classmethod
    def teardown_class(cls):
        '''Ensure that we don't leave stamped
        notes around after the tests are run
        '''
        teardown_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_note(self):
        test_path = '/section/mixed.note'
        note_content = _get_note(notes_directory=CONFIG['notes_directory'],
                                 path=test_path)

        with open(CONFIG['notes_directory'] + test_path, 'r') as f:
            read_content = f.read()

        assert note_content == read_content

    def test_update_note(self):
        test_path = '/section/mixed.note'
        test_content = 'This note has been replaced!'
        _update_note(notes_directory=CONFIG['notes_directory'],
                     file_path=test_path, content=test_content)
        note_content = _get_note(notes_directory=CONFIG['notes_directory'],
                                 path=test_path)
        assert note_content == test_content

    def test_check_links(self):
        invalid_links = _validate_internal_links(
            notes_directory=CONFIG['notes_directory'],
            grep_path=CONFIG['grep_path'])
        assert invalid_links == [
            {
                'line_number': '30',
                'path': '/section/mixed.note',
                'link_target': '/does/not/exist.note',
                'link_text': 'broken'
            }, {
                'line_number': '30',
                'link_target': '/section/mixd.note',
                'link_text': 'typos',
                'path': '/section/mixed.note'
            }
        ]

    def test_check_headings(self):
        pass


class TestNotesOperationsFlask(unittest.TestCase):
    """Test getting stamped todos via the HTTP API"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()
        app = create_app(TEST_CONFIG_PATH)
        cls.api_client = app.test_client()

    @classmethod
    def teardown_class(cls):
        '''Ensure that we don't leave stamped
        notes around after the tests are run
        '''
        teardown_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_get_note(self):
        test_path = '/section/mixed.note'
        params = {'path': test_path}
        note_content = self.api_client.get('/api/v1/note', query_string=params)
        note_content = note_content.data.decode('utf-8')

        with open(CONFIG['notes_directory'] + test_path, 'r') as f:
            read_content = f.read()

        assert note_content == read_content

    def test_update_note(self):
        test_path = '/section/mixed.note'
        test_content = 'This note has been replaced!'
        params = {'path': test_path}
        self.api_client.post('/api/v1/note', query_string=params, data=test_content)
        note_content = self.api_client.get('/api/v1/note', query_string=params)
        note_content = note_content.data.decode('utf-8')
        assert note_content == test_content
