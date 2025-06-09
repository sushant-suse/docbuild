"""Set up logging for the documentation build process."""
import atexit
import logging
import logging.handlers
import os
from pathlib import Path
import queue
from .constants import APP_NAME, BASE_LOG_DIR


LOGGERNAME = f"{APP_NAME}"
"""Name of the main logger for the application."""

LOGFILE = f"{LOGGERNAME}.log"
"""Filename for the main log file."""

KEEP_LOGS = 4
""" Number of log files to keep before rolling over."""

JINJALOGGERNAME = f"{LOGGERNAME}.jinja"
XPATHLOGGERNAME = f"{LOGGERNAME}.xpath"
GITLOGGERNAME = f"{LOGGERNAME}.git"

LOGLEVELS = {
    None: logging.WARNING,  # fallback
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}  # """Map of verbosity levels to logging levels."""


def create_base_log_dir(base_log_dir: str|Path = BASE_LOG_DIR) -> Path:
    """Create the base log directory if it doesn't exist.

    This directory is typically located at :file:`~/.local/state/docbuild/logs`
    as per the XDG Base Directory Specification.

    :param base_log_dir: The base directory where logs should be stored.
        Considers the `XDG_STATE_HOME` environment variable if set.
    :return: The path to the base log directory.
    """
    log_dir = Path(os.getenv("XDG_STATE_HOME", base_log_dir))
    log_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    cliverbosity: int|None,
    fmt: str = "[%(levelname)s] %(funcName)s: %(message)s",
    logdir: str | Path | None = None,
    default_logdir: str | Path = BASE_LOG_DIR,
    use_queue: bool = True,
):
    """Set up logging for the application.

    :param cliverbosity: The verbosity level from the command line.
    :param fmt: The format string for log messages.
    :param logdir: The directory where log files should be stored.
    :param default_logdir: The default directory for logs.
    :param use_queue: Whether to use QueueHandler and QueueListener (for production).
    """
    log_dir = create_base_log_dir(logdir or default_logdir)

    verbosity_index = min((cliverbosity or 0), 2)
    verbosity = LOGLEVELS.get(verbosity_index, logging.WARNING)

    jinja_index = verbosity_index
    xpath_index = verbosity_index + 1
    git_index = verbosity_index + 2

    jinja_level = logging.DEBUG if jinja_index > 2 else LOGLEVELS.get(min(jinja_index, 2), logging.INFO)
    xpath_level = logging.DEBUG if xpath_index > 2 else LOGLEVELS.get(min(xpath_index, 2), logging.INFO)
    git_level = logging.DEBUG if git_index > 2 else LOGLEVELS.get(min(git_index, 2), logging.INFO)

    standard_formatter = logging.Formatter(fmt)
    git_formatter = logging.Formatter("[%(levelname)s] [Git] - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(verbosity)
    console_handler.setFormatter(standard_formatter)

    git_console_handler = logging.StreamHandler()
    git_console_handler.setLevel(git_level)
    git_console_handler.setFormatter(git_formatter)

    log_path = log_dir / LOGFILE
    need_roll = log_path.exists()

    rotating_file_handler = logging.handlers.RotatingFileHandler(
        log_path, backupCount=KEEP_LOGS
    )
    rotating_file_handler.setLevel(logging.DEBUG)
    rotating_file_handler.setFormatter(standard_formatter)

    handlers = []
    listener = None

    if use_queue:
        log_queue = queue.Queue(-1)
        queue_handler = logging.handlers.QueueHandler(log_queue)
        handlers = [queue_handler]
        listener = logging.handlers.QueueListener(
            log_queue,
            console_handler,
            rotating_file_handler,
            respect_handler_level=True,
        )
        listener.start()
        atexit.register(listener.stop)
    else:
        handlers = [console_handler, rotating_file_handler]

    def configure_logger(name: str, level: int):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        for handler in handlers:
            logger.addHandler(handler)
        logger.propagate = False

    configure_logger(LOGGERNAME, verbosity)
    configure_logger(JINJALOGGERNAME, jinja_level)
    configure_logger(XPATHLOGGERNAME, xpath_level)

    git_logger = logging.getLogger(GITLOGGERNAME)
    git_logger.setLevel(git_level)
    git_logger.addHandler(git_console_handler)
    git_logger.propagate = False

    if need_roll:
        rotating_file_handler.doRollover()


def get_effective_level(verbosity: int | None, offset: int = 0) -> int:
    """Return a valid log level, clamped safely.

    :param verbosity: The verbosity level, typically from command
      line arguments (range 0..8)
    :param offset: An offset to apply to the verbosity level.
    :return: The effective log level.
    """
    effective = (verbosity or 0) + offset
    max_key = max(k for k in LOGLEVELS if isinstance(k, int))
    clamped = min(effective, max_key)
    return LOGLEVELS.get(clamped, logging.WARNING)
