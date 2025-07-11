"""Provides context managers."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
import time


@dataclass
class TimerData:
    """Data structure to hold timer information."""

    name: str
    start: float = float('nan')
    end: float = float('nan')
    elapsed: float = float('nan')


def make_timer(
    name: str, method: Callable = time.perf_counter
):  # -> _GeneratorContextManager[TimerData, None, None]
    """Create independant context managers to measure elapsed time.

    Each timer is independent and can be used in a context manager.
    The name is used to identify the timer.

    :param name: Name of the timer.
    :param method: Method to use for measuring time, defaults
        to :func:`time.perf_counter`.
    :return: A context manager that yields a dictionary with start, end,
        and elapsed time.

    .. code-block:: python

        timer = make_timer('example_timer')

        with timer() as timer_data:
            # Code to be timed
            pass

        timer_data.elapsed  # Access the elapsed time
    """
    result = {}

    @contextmanager
    def wrapper() -> Generator[TimerData, None, None]:
        """Context manager to measure elapsed time."""
        nonlocal result
        data = TimerData(name=name)
        result[name] = data
        data.start = method()
        try:
            yield data
        finally:
            data.end = method()
            data.elapsed = data.end - data.start

    return wrapper
