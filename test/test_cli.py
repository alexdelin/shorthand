import logging
import pytest

from shorthand.cli import cli_stamp_notes

from utils import ShorthandTestCase


log = logging.getLogger(__name__)


class TestCLI(ShorthandTestCase, reset_per_method=False):
    """Test command line utilities"""

    def test_stamp_call(self):
        cli_stamp_notes(self.config)
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
