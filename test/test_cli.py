import os
import logging
import pytest

from shorthand.cli import run, cli_stamp_notes

from utils import setup_environment, teardown_environment, setup_logging


ORIGINAL_CONFIG = setup_environment()
setup_logging(ORIGINAL_CONFIG)
log = logging.getLogger(__name__)


def test_setup():

    test_dir = ORIGINAL_CONFIG['notes_directory']
    assert os.path.exists(test_dir)


def test_stamp_call(capfd, caplog):
    _ = setup_environment()
    _ = cli_stamp_notes(ORIGINAL_CONFIG)
    # Validate stdout
    captured = capfd.readouterr()
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
    for record in caplog.records:
        assert record.levelname in ['DEBUG', 'INFO']

    teardown_environment()


def test_cli_empty(capfd):
    '''Test that the usage dialog is shown when run from the CLI
    '''
    with pytest.raises(SystemExit) as e:
        run()
    assert str(e)
    captured = capfd.readouterr()
    assert captured.err.startswith("usage")
