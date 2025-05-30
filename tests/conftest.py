"""Pytest fixtures.

Naming conventions:
- `runner`: provides a `CliRunner` instance for testing CLI commands.
- `default_env_config_filename`: provides a default environment configuration file path.
- `env_content`: provides a default content for the environment configuration file.
- `ctx`: provides a simple dummy context object.
- `context`: provides a `DocBuildContext` instance.
- `fake_*`: Fixtures that patch specific functions or methods.
"""

from pathlib import Path
from typing import Any, Generator, NamedTuple
from unittest.mock import MagicMock

from click.testing import CliRunner
import pytest

import docbuild.cli as cli_module
import docbuild.cli.cli as cli
from docbuild.cli.context import DocBuildContext
from docbuild.constants import DEFAULT_ENV_CONFIG_FILENAME
from tests.common import changedir


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
    """A dummy context class."""

    def __init__(self, obj: Any = None) -> None:  # noqa: ANN401
        self.obj = obj
        self.dry_run = None
        self.verbose = None
        self.envconfigfiles = None
        self.role = None


@pytest.fixture
def ctx() -> type[DummyCtx]:
    """Provide a dummy context object for testing."""
    return DummyCtx


@pytest.fixture
def context() -> DocBuildContext:
    """Provide a DocBuildContext instance for testing."""
    return DocBuildContext()


# --- Mocking fixtures
class MockEnvConfig(NamedTuple):
    """Named tuple to hold the fake env file and mock."""

    fakefile: Path
    mock: MagicMock


class MockCombinedConfig(NamedTuple):
    """Named tuple to hold the fake validate_options."""

    fakefile: Path
    mock: MagicMock
    mock_load_and_merge_configs: MagicMock
    mock_load_single_config: MagicMock


@pytest.fixture
def fake_envfile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Generator[MockEnvConfig, None, None]:
    """Patch the `docbuild.cli.cli.process_envconfig_and_role` function."""
    fakefile = Path('fake_envfile')

    mock = MagicMock(
        return_value=(
            fakefile,
            {
                # Example return value,
                # can be customized with fake_envfile.mock.return_value
                'fake_key': 'fake_value',
            },
        ),
    )

    monkeypatch.setattr(
        cli, "process_envconfig_and_role", mock,
    )

    with changedir(tmp_path):
        yield MockEnvConfig(fakefile, mock)


@pytest.fixture
def fake_confiles(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Generator[MockEnvConfig, None, None]:
    """Patch the `docbuild.cli.cli.load_and_merge_configs` function."""
    with changedir(tmp_path):
        fakefile = Path('fake_config.toml')
        mock = MagicMock(
            return_value=(
                [fakefile],
                {
                    # Example return value,
                    # can be customized with fake_confiles.mock.return_value
                    'fake_config_key': 'fake_config_value'
                },
            ),
        )
        monkeypatch.setattr(
            cli, 'load_and_merge_configs', mock,
        )
        yield MockEnvConfig(fakefile, mock)


@pytest.fixture
def fake_validate_options(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Generator[MockCombinedConfig, None, None]:
    """Patch the `docbuild.cli.validate_options` function.

    Use a temporary directory to simulate the environment.
    """
    with changedir(tmp_path):
        fakefile = Path('fake_validate_options.toml').absolute()

        mock = MagicMock(
            return_value=None,  # This function does not return anything
        )
        monkeypatch.setattr(
            cli_module, 'validate_options', mock,
        )

        mock_load_and_merge_configs = MagicMock(
            return_value=([fakefile], {'fake_key': 'fake_value'})
        )
        monkeypatch.setattr(
            cli_module, 'load_and_merge_configs', mock_load_and_merge_configs,
        )

        mock_load_single_config = MagicMock(return_value={"fake_key": "fake_value"})
        monkeypatch.setattr(
            cli_module, 'load_single_config', mock_load_single_config,
        )

        yield MockCombinedConfig(
            fakefile, mock, mock_load_and_merge_configs, mock_load_single_config
        )
