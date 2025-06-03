from pathlib import Path

import pytest

from docbuild.config import load
from docbuild.config.load import search_config_files
from docbuild.constants import DEFAULT_ENV_CONFIG_FILENAME


def test_search_env_config_file_all_files(monkeypatch: pytest.MonkeyPatch):
    """Test the search_env_config_file function."""
    tmpdirs = [Path("/fake/dir")]
    basenames = ('.config.toml', 'config.toml')

    def mock_exists(self, follow_symlinks: bool = True) -> bool:
        return self.name in basenames
    def mock_is_file(self, follow_symlinks: bool = True) -> bool:
        return True

    monkeypatch.setattr(load.Path, 'exists', mock_exists)
    monkeypatch.setattr(load.Path, 'is_file', mock_is_file)

    result = search_config_files(tmpdirs, basenames)
    assert result == [
        Path("/fake/dir/.config.toml"),
        Path("/fake/dir/config.toml"),
    ]


def test_search_env_config_file_no_files(monkeypatch: pytest.MonkeyPatch):
    """Test the search_env_config_file function."""
    tmpdirs = ["/fake/dir"]
    basenames = ('.config.toml', 'config.toml')

    def mock_exists(self, follow_symlinks: bool = True) -> bool:
        return False
    def mock_is_file(self, follow_symlinks: bool = True) -> bool:
        return True

    monkeypatch.setattr(load.Path, 'exists', mock_exists)
    monkeypatch.setattr(load.Path, 'is_file', mock_is_file)

    result = search_config_files(tmpdirs, basenames)
    assert result == []
