from pathlib import Path
from typing import Any

import pytest

from docbuild.config.load import process_envconfig_and_role
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

    path, container = process_envconfig_and_role(envconfigfile, None)

    assert path == envconfigfile
    assert container == {"specific_key": "specific_value",
                         "common": "overridden_by_file",
                         }


def test_process_with_envconfigfile_not_found(tmp_path: Path):
    """Test when envconfigfile is provided but does not exist."""
    envconfigfile = tmp_path / "non_existent_config.toml"

    with pytest.raises(FileNotFoundError):
        process_envconfig_and_role(envconfigfile, None)


def test_process_with_role_only_valid_role(tmp_path: Path):
    """Test when only a valid role is provided (envconfigfile is None).

    It should use a default configuration path and apply role modifications.
    """
    default_env = tmp_path / Path(DEFAULT_ENV_CONFIG_FILENAME)
    default_env.write_text("""debug = true
    role = "production"
    """)

    with changedir(tmp_path):
        path, data = process_envconfig_and_role(None, "production")

    assert tmp_path / path == default_env
    assert data == {"debug": True, "role": "production"}


def test_process_with_role_only_invalid_role():
    """Test when only an invalid role is provided."""
    with pytest.raises(ValueError, match="Unknown server role"):
        process_envconfig_and_role(None, "unknown")


def test_process_with_both_none(tmp_path: Path):
    """Test when both envconfigfile and role are None.

    It should return a default configuration and default path.
    """
    default_env = tmp_path / Path(DEFAULT_ENV_CONFIG_FILENAME)
    default_env.write_text("")

    with changedir(tmp_path):
        path, actual_container = process_envconfig_and_role(None, None)

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
            process_envconfig_and_role(None, None)
