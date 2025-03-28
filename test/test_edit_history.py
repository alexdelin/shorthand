import os
import time
import logging
from datetime import datetime, UTC

import pytest

from shorthand.edit_history import HISTORY_PATH, _store_history_for_note_edit, ensure_note_version
from utils import ShorthandTestCase


log = logging.getLogger(__name__)


class TestEditHistory(ShorthandTestCase):
    """Test Edit History Tools"""

    def test_storing_daily_note_version(self):
        for test_note in ['/section/mixed.note', '/bugs.note']:
            note_content = self.server.get_note(test_note)
            timestamp = datetime.now(UTC)
            ensure_note_version(notes_directory=self.notes_dir,
                                note_path=test_note,
                                timestamp=timestamp)
            current_utc_day = timestamp.isoformat(timespec='milliseconds')

            # Check the version file was written
            assert os.path.exists(f'{self.notes_dir}/{HISTORY_PATH}/{test_note}/{current_utc_day}.version')

            # Check we can get the version via the API
            note_versions = self.server.list_note_versions(note_path=test_note)
            assert note_versions == [current_utc_day]

            version_content = self.server.get_note_version(test_note, current_utc_day)
            assert version_content == note_content

    def test_storing_create_diffs_for_notes(self):
        self.server.create_file('/new.note')

        note_diffs = self.server.list_diffs_for_note(note_path='/new.note')
        assert len(note_diffs) == 1
        assert note_diffs[0]['diff_type'] == 'create'

        note_diff = self.server.get_note_diff(
            note_path='/new.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff
        assert 'new file mode' in note_diff

    def test_cannot_get_versions_or_diffs_for_resources(self):
        test_note = '/new.txt'
        current_utc_day = datetime.now(UTC).date().isoformat()
        self.server.create_file(test_note)

        assert not os.path.exists(f'{self.notes_dir}/{HISTORY_PATH}/{test_note}/{current_utc_day}.version')

        with pytest.raises(ValueError) as e:
            self.server.list_note_versions(note_path='/new.txt')
        assert e

        with pytest.raises(ValueError) as e:
            self.server.list_diffs_for_note(note_path='/new.txt')
        assert e

    def test_storing_move_diffs(self):
        self.server.create_file('/new.note')
        time.sleep(0.001)
        self.server.move_file_or_directory(source='/new.note', destination='/new2.note')

        note_diffs = self.server.list_diffs_for_note(note_path='/new.note')
        assert len(note_diffs) == 2
        assert note_diffs[0]['diff_type'] == 'move'

        note_diff = self.server.get_note_diff(
            note_path='/new.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff
        assert 'similarity index 100%' in note_diff

    def test_storing_move_diffs_for_file_type_change(self):
        # Start as a resource and move to a note and check that there is a diff
        self.server.create_file('/new.txt')
        time.sleep(0.001)
        self.server.move_file_or_directory(source='/new.txt', destination='/new.note')

        note_diffs = self.server.list_diffs_for_note(note_path='/new.note')
        assert len(note_diffs) == 1
        assert note_diffs[0]['diff_type'] == 'move'

        note_diff = self.server.get_note_diff(
            note_path='/new.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff
        assert 'similarity index 100%' in note_diff

    def test_moving_to_path_with_existing_version(self):
        self.server.create_file('/new.note')
        time.sleep(0.001)
        self.server.update_note('/todos.note', 'foobar')
        time.sleep(0.001)
        self.server.delete_file('/todos.note')
        time.sleep(0.001)
        self.server.move_file_or_directory('/new.note', '/todos.note')

        versions = self.server.list_note_versions('/todos.note')
        assert len(versions) == 2
        # Check that not every version is a start of day version
        assert not all(['T00:00:00.000' in version for version in versions])

        old_path_diffs = self.server.list_diffs_for_note('/new.note')
        assert any([d['diff_type'] == 'move' for d in old_path_diffs])

        new_path_diffs = self.server.list_diffs_for_note('/todos.note')
        assert any([d['diff_type'] == 'move' for d in new_path_diffs])

    def test_storing_diffs_for_directory_move(self):
        self.server.create_file('/section/new.note')
        self.server.create_file('/section/resource.txt')
        self.server.move_file_or_directory('/section', '/newsubdir')

        assert os.path.exists(self.notes_dir + '/.shorthand/history/section/new.note/diffs')
        assert os.path.exists(self.notes_dir + '/.shorthand/history/section/mixed.note/diffs')
        assert os.path.exists(self.notes_dir + '/.shorthand/history/newsubdir/new.note/diffs')
        assert os.path.exists(self.notes_dir + '/.shorthand/history/newsubdir/mixed.note/diffs')
        assert not os.path.exists(self.notes_dir + '/.shorthand/history/section/resource.txt/diffs')
        assert not os.path.exists(self.notes_dir + '/.shorthand/history/newsubdir/resource.txt/diffs')

        assert self.server.list_note_versions('/section/mixed.note')
        assert self.server.list_note_versions('/section/new.note')

        assert self.server.list_diffs_for_note('/section/mixed.note')
        assert len(self.server.list_diffs_for_note('/section/new.note')) == 2

        assert self.server.list_diffs_for_note('/newsubdir/mixed.note')
        assert self.server.list_diffs_for_note('/newsubdir/new.note')

    def test_storing_delete_diffs(self):
        self.server.create_file('/new.note')
        time.sleep(0.001)
        self.server.update_note('/new.note', 'foo bar baz')
        time.sleep(0.001)
        self.server.delete_file('/new.note')

        note_diffs = self.server.list_diffs_for_note('/new.note')
        assert len(note_diffs) == 3
        assert note_diffs[0]['diff_type'] == 'delete'

        note_diff = self.server.get_note_diff(
            note_path='/new.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff
        assert 'deleted file mode' in note_diff

    def test_storing_diffs_for_directory_delete(self):
        self.server.create_file('/section/new.note')

        self.server.delete_directory('/section', recursive=True)
        assert self.server.list_diffs_for_note('/section/mixed.note')
        assert len(self.server.list_diffs_for_note('/section/new.note')) == 2

    def test_storing_edit_diffs(self):
        _store_history_for_note_edit(
            notes_directory=self.notes_dir,
            note_path='/todos.note',
            new_content='foo bar',
            find_path=self.find_path,
            patch_path=self.patch_path)

        note_versions = self.server.list_note_versions('/todos.note')
        assert len(note_versions) == 1

        note_diffs = self.server.list_diffs_for_note('/todos.note')
        assert len(note_diffs) == 1
        assert note_diffs[0]['diff_type'] == 'edit'

        note_diff = self.server.get_note_diff(
            note_path='/todos.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff
        assert 'Author: ' in note_diff
        assert 'Time: ' in note_diff
        assert '---' in note_diff

    def test_merging_edit_diffs(self):
        # Make 3 edits to a note in rapid succession
        self.server.update_note(note_path='/todos.note', content='foo bar')
        time.sleep(0.001)
        self.server.update_note(note_path='/todos.note', content='foo baz bam')
        time.sleep(0.001)
        self.server.update_note(note_path='/todos.note', content='foo baz bam bar')

        note_versions = self.server.list_note_versions(note_path='/todos.note')
        assert len(note_versions) == 1

        note_diffs = self.server.list_diffs_for_note(note_path='/todos.note')
        assert len(note_diffs) == 1

        note_diff = self.server.get_note_diff(
            note_path='/todos.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff

    def test_empty_update(self):
        original = self.server.get_note(note_path='/todos.note')

        # Update a note, but with the existing content
        self.server.update_note(note_path='/todos.note', content=original)

        note_versions = self.server.list_note_versions(note_path='/todos.note')
        assert len(note_versions) == 1

        note_diffs = self.server.list_diffs_for_note(note_path='/todos.note')
        assert len(note_diffs) == 0

    def test_change_and_undo_edit(self):
        original = self.server.get_note(note_path='/todos.note')

        # Create an edit diff
        self.server.update_note(note_path='/todos.note', content='foo bar')
        time.sleep(0.001)
        # Revert so the edit diff is empty
        self.server.update_note(note_path='/todos.note', content=original)

        note_diffs = self.server.list_diffs_for_note(note_path='/todos.note')
        assert len(note_diffs) == 1

        note_diff = self.server.get_note_diff(
            note_path='/todos.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff
        assert 'no changes made' in note_diff

    def test_merge_into_empty_diff(self):
        original = self.server.get_note(note_path='/todos.note')

        # Create an edit diff
        self.server.update_note(note_path='/todos.note', content='foo bar')
        time.sleep(0.001)
        # Revert so the edit diff is empty
        self.server.update_note(note_path='/todos.note', content=original)
        time.sleep(0.001)
        # Merge a new change into the empty diff
        self.server.update_note(note_path='/todos.note', content='baz')

        note_diffs = self.server.list_diffs_for_note(note_path='/todos.note')
        assert len(note_diffs) == 1

        note_diff = self.server.get_note_diff(
            note_path='/todos.note',
            timestamp=note_diffs[0]['timestamp'],
            diff_type=note_diffs[0]['diff_type'])
        assert note_diff
        assert '---' in note_diff

    def test_no_history_when_disabled(self):
        self.server.update_config({'track_edit_history': False})

        self.server.create_file('/new.note')
        self.server.update_note('/todos.note', 'New Content')
        self.server.delete_file('/bugs.note')
        self.server.move_file_or_directory('/locations.note', '/places.note')

        assert not self.server.list_note_versions('/new.note')
        assert not self.server.list_note_versions('/todos.note')
        assert not self.server.list_note_versions('/bugs.note')
        assert not self.server.list_note_versions('/locations.note')
        assert not self.server.list_note_versions('/places.note')

        assert not self.server.list_diffs_for_note('/new.note')
        assert not self.server.list_diffs_for_note('/todos.note')
        assert not self.server.list_diffs_for_note('/bugs.note')
        assert not self.server.list_diffs_for_note('/locations.note')
        assert not self.server.list_diffs_for_note('/places.note')
