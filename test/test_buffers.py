import time
import random
import logging

import unittest
import pytest

from shorthand import ShorthandServer
from utils import TEST_CONFIG_PATH, setup_environment, validate_setup


log = logging.getLogger(__name__)

NUM_TEST_BUFFERS = 3


class TestBuffers(unittest.TestCase):
    """Test buffer management functionality of the library"""

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']
        cls.server = ShorthandServer(TEST_CONFIG_PATH)

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_create_and_list_buffers(self):

        # Basic Test for creating buffers
        buffer_ids = []
        for i in range(NUM_TEST_BUFFERS):
            if i != 0:
                time.sleep(0.002)
            buffer_id = self.server.new_buffer()
            assert buffer_id
            buffer_ids.append(buffer_id)
        assert len(buffer_ids) == len(set(buffer_ids))
        assert len(buffer_ids) == NUM_TEST_BUFFERS

        # Basic Test for retrieving buffers
        buffers_found = self.server.list_buffers()
        assert set(buffers_found) == set(buffer_ids)

        # Test that two buffers can't be created in the same second.
        # May be flaky in extremely show situations
        with pytest.raises(ValueError) as e:
            for i in range(NUM_TEST_BUFFERS):
                buffer_id = self.server.new_buffer()
                assert buffer_id
        assert 'already exists' in str(e.value)

    def test_update_and_get_buffers(self):

        # Get Empty Contents of a single buffer
        first_buffer = self.server.list_buffers()[0]
        content = self.server.get_buffer_content(first_buffer)
        assert content == ''

        # Try to get the content of a non-existent buffer
        with pytest.raises(ValueError) as e:
            _ = self.server.get_buffer_content('foobar')
        assert 'not found' in str(e.value)

        # Write some content into a buffer
        TEST_CONTENT = 'Test Content'
        self.server.update_buffer_content(first_buffer, TEST_CONTENT)

        # Get the buffer's contents to check for the added content
        updated_content = self.server.get_buffer_content(first_buffer)
        assert updated_content == TEST_CONTENT

    def test_delete_buffers(self):
        all_buffers = self.server.list_buffers()
        buffer_to_delete = random.choice(all_buffers)
        self.server.delete_buffer(buffer_to_delete)

        updated_buffers = self.server.list_buffers()
        assert buffer_to_delete not in updated_buffers
        assert len(updated_buffers) == len(all_buffers) - 1

    def test_write_buffer_to_file(self):
        # Write some test content into a buffer
        first_buffer = self.server.list_buffers()[0]
        TEST_CONTENT = 'Test Content'
        self.server.update_buffer_content(first_buffer, TEST_CONTENT)

        # Append the Buffer to an existing note file
        NOTE_PATH = '/todos.note'
        self.server.write_buffer(first_buffer, NOTE_PATH)

        # Read the note file and check for the added content
        updated_note = self.server.get_note(NOTE_PATH)
        assert updated_note.endswith(TEST_CONTENT)
