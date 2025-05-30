"""Pytest fixtures."""

from pathlib import Path
from typing import Any

from click.testing import CliRunner
import pytest

from docbuild.constants import DEFAULT_ENV_CONFIG_FILENAME


@pytest.fixture(scope="function")
def runner() -> CliRunner:
    """Provide a CliRunner instance for testing."""
    return CliRunner()


@pytest.fixture(scope="function")
def default_env_config_filename(tmp_path: Path) -> Path:
    """Provide a default env config file path."""
    envfile = tmp_path / DEFAULT_ENV_CONFIG_FILENAME
    envfile.write_text("")
    return envfile


@pytest.fixture(scope="function")
def env_content(default_env_config_filename: Path) -> Path:
    """Provide a default content for the env config file."""
    content = """# Test file
[paths]
config_dir = "/etc/docbuild"
repo_dir = "/data/docserv/repos/permanent-full/"
temp_repo_dir = "/data/docserv/repos/temporary-branches/"

[paths.tmp]
tmp_base_path = "/tmp"
tmp_path = "{tmp_base_path}/doc-example-com"
"""
    default_env_config_filename.write_text(content)
    return default_env_config_filename


class DummyCtx:
    """A dummy context class for testing purposes."""

    def __init__(self, obj: Any) -> None:  # noqa: ANN401
        self.obj = obj


@pytest.fixture
def ctx() -> DummyCtx:
    """Provide a dummy context object for testing."""
    return DummyCtx
