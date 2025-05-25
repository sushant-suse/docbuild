
from contextlib import contextmanager
import os
from pathlib import Path


@contextmanager
def changedir(path: str | Path):
    """
    Contextmanager to change directory and preserve it afterwards.
    """
    pwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(pwd)