import time
import random
import logging

import pytest

from utils import ShorthandTestCase


log = logging.getLogger(__name__)

NUM_TEST_BUFFERS = 3


class TestBuffers(ShorthandTestCase, reset_per_method=False):
    """Test buffer management functionality of the library"""

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
