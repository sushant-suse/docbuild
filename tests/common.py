"""Common utilities for tests."""

from collections.abc import Generator
from contextlib import contextmanager
import os
from pathlib import Path
from typing import Any


@contextmanager
def changedir(path: str | Path) -> Generator[None, Any, None]:
    """Switch to a new directory and restore the original one afterwards."""
    pwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(pwd)
