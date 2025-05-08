from pathlib import Path

import pytest

from docbuild.config import load_app_config
from docbuild.constants import APP_CONFIG_FILENAME, APP_NAME



def write_toml_file(path: Path, data: str):
    path.write_text(data)


def test_load_app_single_config(tmp_path):
    configpath = tmp_path / "etc" / APP_NAME
    configpath.mkdir(parents=True)
    write_toml_file(configpath / APP_CONFIG_FILENAME,
    """[server]
name = "localhost"
port = 1234
"""
    )
    config = load_app_config(configpath)
    assert config
    assert config == {"server": {"name": "localhost", "port": 1234}}


def test_load_app_multiple_configs(tmp_path):
    system_path = tmp_path / "etc" / APP_NAME
    user_path = tmp_path / "home" / "test" / ".config" / APP_NAME
    local_path = tmp_path

    system_path.mkdir(parents=True)
    user_path.mkdir(parents=True)
    # local_path.mkdir(parents=True)

    write_toml_file(system_path / APP_CONFIG_FILENAME,
        """[server]
name = "localhost"
port = 1234
""")
    write_toml_file(user_path / APP_CONFIG_FILENAME,
        """[server]
[db]
name = "mydatabase"
""")
    write_toml_file(
        local_path / APP_CONFIG_FILENAME,
        """[server]
port = 4321""",
    )

    config = load_app_config(system_path, user_path, local_path)
    assert config == {
        "server": {"name": "localhost", "port": 4321},
        "db": {"name": "mydatabase"}
    }


def test_load_app_with_one_config_not_exists(tmp_path):
    system_path = tmp_path / "etc" / APP_NAME
    missing_path = tmp_path / "home" / "test" / ".config" / APP_NAME

    system_path.mkdir(parents=True)
    missing_path.mkdir(parents=True)

    write_toml_file(
        system_path / APP_CONFIG_FILENAME,
        """[server]
name = "localhost"
port = 1234
""",
    )

    config = load_app_config(system_path, missing_path)
    assert config == {"server": {"name": "localhost", "port": 1234}}


def test_load_app_with_empty_args(tmp_path):
    system_path = tmp_path / "etc" / APP_NAME

    system_path.mkdir(parents=True)

    write_toml_file(
        system_path / APP_CONFIG_FILENAME,
        """[server]
name = "localhost"
port = 1234
""",
    )
    config = load_app_config(default=(system_path,))
    assert config == {"server": {"name": "localhost", "port": 1234}}
