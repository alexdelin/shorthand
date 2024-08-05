import os
import logging
import pytest
import unittest

from shorthand.cli import run, cli_stamp_notes

from utils import setup_environment, teardown_environment, setup_logging, \
                  validate_setup


log = logging.getLogger(__name__)


class TestCLI(unittest.TestCase):
    """Test command line utilities"""

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog, capfd):
        self._caplog = caplog
        self._capfd = capfd

    @classmethod
    def setup_class(cls):
        # ensure that we have a clean environment before running any tests
        cls.config = setup_environment()
        cls.notes_dir = cls.config['notes_directory']
        cls.cache_dir = cls.config['cache_directory']
        cls.grep_path = cls.config['grep_path']
        cls.find_path = cls.config['find_path']

    def setup_method(self, method):
        '''Validate that the environment has been set up correctly
        '''
        validate_setup()

    def test_stamp_call(self):
        _ = setup_environment()
        _ = cli_stamp_notes(self.config)
        # Validate stdout
        captured = self._capfd.readouterr()
        old_line_count, new_line_count, file_count = 0, 0, 0
        for line in captured.out.split('\n'):
            if '(old):' in line:
                old_line_count += 1
            if '(new):' in line:
                new_line_count += 1
            if line.startswith('<<--') and line.endswith('-->>'):
                file_count += 1
        assert new_line_count == old_line_count
        assert file_count == 4

        # Validate that we only get DEBUG and INFO log messages
        for record in self._caplog.records:
            assert record.levelname in ['DEBUG', 'INFO']

        teardown_environment()


# def test_cli_empty(capfd):
#     '''Test that the usage dialog is shown when run from the CLI
#     '''
#     with pytest.raises(SystemExit) as e:
#         run()
#     assert str(e)
#     captured = capfd.readouterr()
#     assert captured.err.startswith("usage")
