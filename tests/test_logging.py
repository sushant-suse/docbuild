import logging
from pathlib import Path
import stat

import pytest

from docbuild.constants import APP_NAME
from docbuild.logging import (
    GITLOGGERNAME,
    JINJALOGGERNAME,
    LOGFILE,
    LOGGERNAME,
    XPATHLOGGERNAME,
    create_base_log_dir,
    get_effective_level,
    setup_logging,
)


def test_create_base_log_dir_with_tmp_path(tmp_path: Path):
    """Test the creation of the base log directory."""
    base_log_dir = tmp_path / 'state' / APP_NAME / 'logs'

    # Call the function
    result = create_base_log_dir(base_log_dir)

    # Check if the directory was created correctly
    assert result == base_log_dir
    assert result.exists()
    assert result.is_dir()
    permissions = stat.S_IMODE(result.stat().st_mode)
    assert permissions == 0o700, f'Expected 0700, got {oct(permissions)}'


def test_create_base_log_dir_with_env_var(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test the creation of the base log directory with an environment variable."""
    base_log_dir = tmp_path / 'state' / APP_NAME / 'logs'
    monkeypatch.setenv('XDG_STATE_HOME', str(base_log_dir))
    result = create_base_log_dir()

    assert result == base_log_dir
    assert result.exists()
    assert result.is_dir()
    permissions = stat.S_IMODE(result.stat().st_mode)
    assert permissions == 0o700, f'Expected 0700, got {oct(permissions)}'


@pytest.mark.parametrize(
    'cliverbosity, expected_level',
    [
        (None, logging.WARNING),
        (0, logging.WARNING),
        (1, logging.INFO),
        (2, logging.DEBUG),
        (3, logging.DEBUG),
        (10, logging.DEBUG),  # cap at max level
    ],
)
def test_get_effective_levels(cliverbosity: None | int, expected_level: int):
    result = get_effective_level(cliverbosity)
    assert result == expected_level, (
        f'Expected {expected_level} for verbosity {cliverbosity}, got {result}'
    )


@pytest.mark.parametrize(
    'cliverbosity, expected_level',
    [
        (None, logging.WARNING),
        (0, logging.WARNING),
        (1, logging.INFO),
        (2, logging.DEBUG),
        (999, logging.DEBUG),  # cap at max level
    ],
)
def test_logger_levels(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    cliverbosity: None | int,
    expected_level: int,
):
    monkeypatch.delenv('XDG_STATE_HOME', raising=False)

    setup_logging(
        cliverbosity=cliverbosity,
        logdir=tmp_path,
        fmt='[%(levelname)s] %(name)s: %(message)s',
        use_queue=False,
    )

    app_logger = logging.getLogger(LOGGERNAME)
    jinja_logger = logging.getLogger(JINJALOGGERNAME)
    xpath_logger = logging.getLogger(XPATHLOGGERNAME)
    git_logger = logging.getLogger(GITLOGGERNAME)

    assert app_logger.getEffectiveLevel() == expected_level
    # jinja and others may use higher level:
    assert jinja_logger.getEffectiveLevel() <= expected_level
    assert xpath_logger.getEffectiveLevel() <= expected_level
    assert git_logger.getEffectiveLevel() <= expected_level


@pytest.mark.parametrize(
    'logger_name',
    [
        LOGGERNAME,
        JINJALOGGERNAME,
        XPATHLOGGERNAME,
    ],
)
def test_logging_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], logger_name: str
):
    setup_logging(
        cliverbosity=2,
        logdir=tmp_path,
        fmt='%(levelname)s:%(message)s',
        use_queue=False,
    )
    logger = logging.getLogger(logger_name)
    logger.debug('debug message')

    captured = capsys.readouterr()

    assert 'debug message' in captured.err


def test_setup_logging_with_queue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Ensure the setup completes successfully when use_queue is True."""
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    setup_logging(cliverbosity=2, use_queue=True, logdir=tmp_path)

    logger = logging.getLogger('docbuild')
    logger.debug('queue-based logging works')

    # Since we cannot capture QueueHandler logs via caplog, we check handler types.
    assert any(isinstance(h, logging.handlers.QueueHandler) for h in logger.handlers)


def test_setup_logging_triggers_rollover(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test setup_logging triggers a rollover when logfile already exists."""
    logdir = tmp_path / 'logs'
    logdir.mkdir(parents=True, exist_ok=True)
    log_path = logdir / LOGFILE

    # Create the log file to trigger `need_roll = True`
    log_path.write_text('existing content')

    monkeypatch.setenv('XDG_STATE_HOME', str(logdir))
    setup_logging(cliverbosity=2, use_queue=False, logdir=logdir)

    # After rollover, a new empty log file should exist
    assert log_path.exists()
    assert log_path.read_text() == '' or 'existing content' not in log_path.read_text()
