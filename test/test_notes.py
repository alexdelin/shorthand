import logging
import unittest
import pytest
import random

from shorthand.notes import _get_note, _update_note, \
                            _validate_internal_links, \
                            _append_to_note, _get_links, \
                            _get_backlinks
from shorthand.utils.filesystem import _create_file, _delete_file
from shorthand.web.app import create_app

from utils import ShorthandTestCase, setup_environment, teardown_environment, validate_setup, \
                  TEST_CONFIG_PATH
from model import ShorthandModel
from results_unstamped import ALL_LINKS


log = logging.getLogger(__name__)
MODEL = ShorthandModel()


class TestNotesOperations(ShorthandTestCase):
    """Test basic operations on note files via the library"""

    def test_get_note(self):
        test_path = '/section/mixed.note'
        note_content = _get_note(notes_directory=self.notes_dir,
                                 path=test_path)

        with open(self.notes_dir + test_path, 'r') as f:
            read_content = f.read()

        assert note_content == read_content

        # Test error handling for invalid notes paths
        with pytest.raises(ValueError) as e:
            _get_note(notes_directory=self.notes_dir,
                      path='/doesnt-exist.note')
        assert 'does not exist' in str(e.value)

    def test_create_note(self):
        new_note_path = '/new.note'
        _create_file(notes_directory=self.notes_dir,
                     file_path=new_note_path)
        note_content = _get_note(notes_directory=self.notes_dir,
                                 path=new_note_path)
        assert isinstance(note_content, str)

        # Test handling for specifying a path to an existing note
        with pytest.raises(ValueError) as e:
            _create_file(notes_directory=self.notes_dir,
                         file_path='/todos.note')
        assert 'already exists' in str(e.value)

    def test_delete_note(self):
        test_path = '/questions.note'
        assert _get_note(notes_directory=self.notes_dir,
                         path=test_path)
        _delete_file(notes_directory=self.notes_dir,
                     file_path=test_path)
        with pytest.raises(ValueError) as e:
            _get_note(notes_directory=self.notes_dir,
                      path=test_path)
        assert 'does not exist' in str(e.value)

    def test_update_note(self):
        test_path = '/section/mixed.note'
        test_content = 'This note has been replaced!'
        _update_note(notes_directory=self.notes_dir,
                     file_path=test_path, content=test_content)
        note_content = _get_note(notes_directory=self.notes_dir,
                                 path=test_path)
        assert note_content == test_content
        #TODO - Test that updating a note that doesn't exist throws the right error
        #TODO - Test that updating a note with empty content still works

    def test_append_to_note(self):
        test_path = '/todos.note'
        test_content = '## A new section\nwith some more content'
        original_content = _get_note(notes_directory=self.notes_dir,
                                     path=test_path)
        _append_to_note(notes_directory=self.notes_dir,
                        note_path=test_path, content=test_content,
                        blank_lines=1)
        updated_note = _get_note(notes_directory=self.notes_dir,
                                 path=test_path)
        assert original_content in updated_note
        assert test_content in updated_note
        assert updated_note == original_content + '\n\n' + test_content
        #TODO - Test that number of blank lines is resprected
        #TODO - Test that specifying a note that doesn't exist throws an error

    def test_check_headings(self):
        pass


class TestLinkOperations(ShorthandTestCase, reset_per_method=False):
    """Test basic operations on links via the library"""

    def test_validate_internal_links(self):
        invalid_links = _validate_internal_links(
            notes_directory=self.notes_dir,
            grep_path=self.grep_path)
        _invalid_links = [link for link in ALL_LINKS if not link['valid']]
        self.assertCountEqual(invalid_links, _invalid_links)

        source = '/section/mixed.note'
        invalid_links = _validate_internal_links(
            notes_directory=self.notes_dir,
            source=source,
            grep_path=self.grep_path)
        _invalid_links = [link for link in ALL_LINKS
                          if not link['valid'] and link['source'] == source]
        self.assertCountEqual(invalid_links, _invalid_links)


    def test_get_all_links(self):
        # Test Getting all notes
        all_links = _get_links(notes_directory=self.notes_dir,
                               source=None, target=None, note=None,
                               include_external=True, include_invalid=True,
                               grep_path=self.grep_path)
        self.assertCountEqual(all_links, ALL_LINKS)

    def test_filtering_links(self):
        # Test filtering for source
        for test_source in ['/section/mixed.note', '/todos.note',
                            '/questions.note', '/does-not-exist.note']:
            params = {
                'notes_directory': self.notes_dir,
                'source': test_source,
                'target': None,
                'note': None,
                'include_external': True,
                'include_invalid': True,
                'grep_path': self.grep_path
            }
            self.assertCountEqual(_get_links(**params),
                                  MODEL.get_links(**params))

        # Test filtering for target
        for test_target in ['/definitions.note', '/section/mixed.note',
                            '/does-not-exist.note']:
            params = {
                'notes_directory': self.notes_dir,
                'source': None,
                'target': test_target,
                'note': None,
                'include_external': True,
                'include_invalid': True,
                'grep_path': self.grep_path
            }
            self.assertCountEqual(_get_links(**params),
                                  MODEL.get_links(**params))

        # Test filtering for note
        for test_note in []:
            params = {
                'notes_directory': self.notes_dir,
                'source': None,
                'target': None,
                'note': test_note,
                'include_external': True,
                'include_invalid': True,
                'grep_path': self.grep_path
            }
            self.assertCountEqual(_get_links(**params),
                                  MODEL.get_links(**params))

    def test_get_links_model(self):
        sources = [None, '/section/mixed.note', '/todos.note',
                   '/questions.note', '/does-not-exist.note']
        targets = [None, '/definitions.note', '/section/mixed.note',
                   '/does-not-exist.note', '/bugs.note', 'https://nytimes.com']
        notes = sources + targets
        external_options = [True, False]
        invalid_options = [True, False]

        for _ in range(50):
            use_note = random.choice((True, False))
            args = {
                'notes_directory': self.notes_dir,
                'source': random.choice(sources) if not use_note else None,
                'target': random.choice(targets) if not use_note else None,
                'note': random.choice(notes) if use_note else None,
                'include_external': random.choice(external_options),
                'include_invalid': random.choice(invalid_options),
                'grep_path': self.grep_path
            }
            log.debug(f"args: {args}")
            print(args)
            self.assertCountEqual(_get_links(**args),
                                  MODEL.get_links(**args))

    def test_get_backlinks(self):

        targets = ['/definitions.note', '/section/mixed.note',
                   '/does-not-exist.note', '/bugs.note']
        for target in targets:
            args = {
                'notes_directory': self.notes_dir,
                'note_path': target,
                'grep_path': self.grep_path
            }
            log.debug(f"args: {args}")
            self.assertCountEqual(_get_backlinks(**args),
                                  MODEL.get_backlinks(**args))

        # Ensure you can't get backlinks for an external target
        backlinks = _get_backlinks(notes_directory=self.notes_dir,
                                   note_path='https://nytimes.com')
        assert len(backlinks) == 0


class TestNotesOperationsFlask(ShorthandTestCase, reset_per_method=False, include_flask_client=True):
    """Test getting stamped todos via the HTTP API"""

    def test_get_note(self):
        test_path = '/section/mixed.note'
        params = {'path': test_path}
        note_content = self.api_client.get('/api/v1/note', query_string=params)
        note_content = note_content.data.decode('utf-8')

        with open(self.notes_dir + test_path, 'r') as f:
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
