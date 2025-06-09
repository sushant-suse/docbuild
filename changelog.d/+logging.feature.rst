Implement logging

Add new functions:

* :func:`~docbuild.logging.create_base_log_dir`: Create the base log directory if it doesn't exist.
* :func:`~docbuild.logging.setup_logging`: Set up logging for the application.
* :func:`~docbuild.logging.get_effective_level`: Return a valid log level, clamped safely.

The `setup_logging` sets different loggers for the app itself, for Jinja,
XPath, and Git.