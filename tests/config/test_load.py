from pathlib import Path
from typing import Any

import pytest

import docbuild.config.load as load_mod
from docbuild.config.load import handle_config, process_envconfig
from docbuild.constants import DEFAULT_ENV_CONFIG_FILENAME

from ..common import changedir

# Define a placeholder for the expected Container type for clarity in tests
Container = dict[str, Any]


def test_process_with_envconfigfile_only(tmp_path: Path):
    """Test when only envconfigfile is provided (role is None).

    It should load the configuration from the specified file.
    """
    config_file_content = (
        'specific_key = "specific_value"\ncommon = "overridden_by_file"'
    )
    envconfigfile = tmp_path / "custom_config.toml"
    envconfigfile.write_text(config_file_content)

    path, container = process_envconfig(envconfigfile)

    assert path == envconfigfile
    assert container == {"specific_key": "specific_value",
                         "common": "overridden_by_file",
                         }


def test_process_with_envconfigfile_not_found(tmp_path: Path):
    """Test when envconfigfile is provided but does not exist."""
    envconfigfile = tmp_path / "non_existent_config.toml"

    with pytest.raises(FileNotFoundError):
        process_envconfig(envconfigfile)


def test_process_with_role_only_valid_role(tmp_path: Path):
    """Test when only a valid role is provided (envconfigfile is None).

    It should use a default configuration path and apply role modifications.
    """
    default_env = tmp_path / Path(DEFAULT_ENV_CONFIG_FILENAME)
    default_env.write_text("""debug = true
    role = "production"
    """)

    with changedir(tmp_path):
        path, data = process_envconfig(None)

    assert tmp_path / path == default_env
    assert data == {"debug": True, "role": "production"}



def test_process_with_both_none(tmp_path: Path):
    """Test when both envconfigfile and role are None.

    It should return a default configuration and default path.
    """
    default_env = tmp_path / Path(DEFAULT_ENV_CONFIG_FILENAME)
    default_env.write_text("")

    with changedir(tmp_path):
        path, actual_container = process_envconfig(None)

    assert tmp_path / path == default_env
    assert actual_container == {}


def test_process_with_both_envconfigfile_and_role_provided(tmp_path: Path):
    """Test when both envconfigfile and role are provided (non-None).

    This should raise a ValueError based on the constraint "One of the
    arguments has to be None".
    """
    with changedir(tmp_path):
        with pytest.raises(
            ValueError, match="Could not find default ENV configuration file",
        ):
            process_envconfig(None)


def test_handle_config_user_path(monkeypatch):
    config_file = Path("/fake/path/myconfig.toml")
    called = {}
    def fake_load_single_config(path):
        called['path'] = path
        return {'section': {'key': 'value'}}
    monkeypatch.setattr(load_mod, "load_single_config", fake_load_single_config)
    result = handle_config(config_file, [], None, None, None)
    assert result[0] == (config_file,)
    assert result[1] == {'section': {'key': 'value'}}
    assert result[2] is False
    assert called['path'] == config_file


def test_handle_config_user_path_str(monkeypatch):
    # Accepts a string as user_path
    config_file = "/fake/path/myconfig.toml"
    called = {}
    def fake_load_single_config(path):
        called['path'] = path
        return {'section': {'key': 'value'}}
    monkeypatch.setattr(load_mod, "load_single_config", fake_load_single_config)
    result = handle_config(config_file, [], None, None, None)
    # Should convert to Path
    assert result[0] == (Path(config_file),)
    assert result[1] == {'section': {'key': 'value'}}
    assert result[2] is False
    assert called['path'] == config_file


def test_handle_config_search_dirs_and_basenames(monkeypatch):
    search_dir = Path("/fake/dir")
    basename = "found.toml"
    config_file = search_dir / basename
    def fake_exists(self):
        return self == config_file
    monkeypatch.setattr(Path, "exists", fake_exists)
    def fake_load_single_config(path):
        return {'section': {'key': 'found'}}
    monkeypatch.setattr(load_mod, "load_single_config", fake_load_single_config)
    result = handle_config(None, [search_dir], [basename], None, None)
    assert result[0] == (config_file,)
    assert result[1] == {'section': {'key': 'found'}}
    assert result[2] is False


def test_handle_config_basename_and_default_filename(monkeypatch):
    # Both basenames and default_filename are given, only basenames should be used
    search_dir = Path("/fake/dir")
    basename = "found.toml"
    default_filename = "default.toml"
    config_file = search_dir / basename
    def fake_exists(self):
        return self == config_file
    monkeypatch.setattr(Path, "exists", fake_exists)
    def fake_load_single_config(path):
        return {'section': {'key': 'found'}}
    monkeypatch.setattr(load_mod, "load_single_config", fake_load_single_config)
    # default_filename should be ignored if basenames is not None
    result = handle_config(None, [search_dir], [basename], default_filename, None)
    assert result[0] == (config_file,)
    assert result[1] == {'section': {'key': 'found'}}
    assert result[2] is False


def test_handle_config_search_dirs_and_default_filename(monkeypatch):
    search_dir = Path("/fake/dir")
    default_filename = "default.toml"
    config_file = search_dir / default_filename
    def fake_exists(self):
        return self == config_file
    monkeypatch.setattr(Path, "exists", fake_exists)
    def fake_load_single_config(path):
        return {'section': {'key': 'default'}}
    monkeypatch.setattr(load_mod, "load_single_config", fake_load_single_config)
    result = handle_config(None, [search_dir], None, default_filename, None)
    assert result[0] == (config_file,)
    assert result[1] == {'section': {'key': 'default'}}
    assert result[2] is False


def test_handle_config_empty_search_dirs(monkeypatch):
    # If search_dirs is empty, should return default
    default = {'default': True}
    result = handle_config(None, [], ["nope.toml"], None, default)
    assert result[0] is None
    assert result[1] == default
    assert result[2] is True


def test_handle_config_empty_basenames_and_default_filename(monkeypatch):
    # If both basenames and default_filename are None, should return default
    default = {'default': True}
    result = handle_config(None, [Path("/any")], None, None, default)
    assert result[0] is None
    assert result[1] == default
    assert result[2] is True


def test_handle_config_not_found_returns_default(monkeypatch):
    # Patch Path.exists to always return False
    monkeypatch.setattr(Path, "exists", lambda self: False)
    default = {'default': True}
    result = handle_config(None, [Path("/nonexistent")], ["nope.toml"], None, default)
    assert result[0] is None
    assert result[1] == default
    assert result[2] is True


def test_handle_config_multiple_basenames_one_exists(monkeypatch):
    search_dir = Path("/fake/dir")
    basenames = ["notfound.toml", "found.toml"]
    found_file = search_dir / basenames[1]
    # Patch Path.exists: only found_file returns True
    def fake_exists(self):
        return self == found_file
    monkeypatch.setattr(Path, "exists", fake_exists)
    def fake_load_single_config(path):
        return {'section': {'key': 'found'}}
    monkeypatch.setattr(load_mod, "load_single_config", fake_load_single_config)
    result = handle_config(None, [search_dir], basenames, None, None)
    assert result[0] == (found_file,)
    assert result[1] == {'section': {'key': 'found'}}
    assert result[2] is False


def test_handle_config_first_basename_exists(monkeypatch):
    search_dir = Path("/fake/dir")
    basenames = ["first.toml", "second.toml"]
    first_file = search_dir / basenames[0]
    # Patch Path.exists: only first_file returns True
    def fake_exists(self):
        return self == first_file
    monkeypatch.setattr(Path, "exists", fake_exists)
    def fake_load_single_config(path):
        return {'section': {'key': 'first'}}
    monkeypatch.setattr(load_mod, "load_single_config", fake_load_single_config)
    result = handle_config(None, [search_dir], basenames, None, None)
    assert result[0] == (first_file,)
    assert result[1] == {'section': {'key': 'first'}}
    assert result[2] is False
