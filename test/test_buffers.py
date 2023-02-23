import time
import random
import logging

import unittest
import pytest

from shorthand.utils.buffers import _new_buffer, _get_buffers, \
                                    _get_buffer_content, _write_buffer, \
                                    _update_buffer_content, _delete_buffer
from shorthand.notes import _get_note
from utils import setup_environment, validate_setup, setup_logging


CONFIG = setup_environment()
log = logging.getLogger(__name__)

NUM_TEST_BUFFERS = 3


class TestBuffers(unittest.TestCase):
    """Test buffer management functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        _ = setup_environment()

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_create_and_list_buffers(self):

        # Basic Test for creating buffers
        buffer_ids = []
        for i in range(NUM_TEST_BUFFERS):
            if i != 0:
                time.sleep(1)
            buffer_id = _new_buffer(CONFIG['cache_directory'])
            assert buffer_id
            buffer_ids.append(buffer_id)
        assert len(buffer_ids) == len(set(buffer_ids))
        assert len(buffer_ids) == NUM_TEST_BUFFERS

        # Basic Test for retrieving buffers
        buffers_found = _get_buffers(CONFIG['cache_directory'])
        assert set(buffers_found) == set(buffer_ids)

        # Test that two buffers can't be created in the same second.
        # May be flaky in extremely show situations
        with pytest.raises(ValueError) as e:
            for i in range(NUM_TEST_BUFFERS):
                buffer_id = _new_buffer(CONFIG['cache_directory'])
                assert buffer_id
        assert 'already exists' in str(e.value)

    def test_update_and_get_buffers(self):

        # Get Empty Contents of a single buffer
        first_buffer = _get_buffers(CONFIG['cache_directory'])[0]
        content = _get_buffer_content(CONFIG['cache_directory'], first_buffer)
        assert content == ''

        # Try to get the content of a non-existent buffer
        with pytest.raises(ValueError) as e:
            _ = _get_buffer_content(CONFIG['cache_directory'], 'foobar')
        assert 'not found' in str(e.value)

        # Write some content into a buffer
        TEST_CONTENT = 'Test Content'
        _update_buffer_content(CONFIG['cache_directory'], first_buffer,
                               TEST_CONTENT)

        # Get the buffer's contents to check for the added content
        updated_content = _get_buffer_content(CONFIG['cache_directory'],
                                              first_buffer)
        assert updated_content == TEST_CONTENT

    def test_delete_buffers(self):
        all_buffers = _get_buffers(CONFIG['cache_directory'])
        buffer_to_delete = random.choice(all_buffers)
        _delete_buffer(CONFIG['cache_directory'], buffer_to_delete)

        updated_buffers = _get_buffers(CONFIG['cache_directory'])
        assert buffer_to_delete not in updated_buffers
        assert len(updated_buffers) == len(all_buffers) - 1

    def test_write_buffer_to_file(self):
        # Write some test content into a buffer
        first_buffer = _get_buffers(CONFIG['cache_directory'])[0]
        TEST_CONTENT = 'Test Content'
        _update_buffer_content(CONFIG['cache_directory'], first_buffer,
                               TEST_CONTENT)

        # Append the Buffer to an existing note file
        NOTE_PATH = '/todos.note'
        _write_buffer(CONFIG['cache_directory'], CONFIG['notes_directory'],
                      first_buffer, NOTE_PATH)

        # Read the note file and check for the added content
        updated_note = _get_note(CONFIG['notes_directory'], NOTE_PATH)
        assert updated_note.endswith(TEST_CONTENT)
