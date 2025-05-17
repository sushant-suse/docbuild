from contextlib import contextmanager
import os
from pathlib import Path
from unittest.mock import ANY, call, MagicMock

import pytest
# from docbuild.cli.cli import cli
from docbuild.constants import ENV_CONFIG_FILENAME
from docbuild.cli.showconfig.env import env
from docbuild.cli.context import DocBuildContext


@contextmanager
def chdir(new_dir: Path | str):
    """Context manager to save directory"""
    # Save current directory
    old_dir = Path.cwd()

    try:
        # Change to the new directory
        os.chdir(new_dir)
        yield  # yield control back to the caller
    finally:
        # Change back to the old directory
        os.chdir(old_dir)


def test_showconfig_env_help_option(runner):
    result = runner.invoke(env, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "[mutually_exclusive]" in result.output
    assert "--config" in result.output
    assert "--role" in result.output


def test_showconfig_env_config_option(runner):
    configfile = Path(__file__).parent / "sample-env.toml"
    context = DocBuildContext()
    result = runner.invoke(env, ["--config", str(configfile)], obj=context)
    assert result.exit_code == 0
    assert "# Config file " in result.output
    assert context.configfile == configfile


def test_showconfig_env_config_option_invalidfile(runner, tmp_path):
    content = """
[paths]
config_dir = "/etc/docbuild"
repo_dir = "/data/docserv/repos/permanent-full/"
temp_repo_dir = "/data/docserv/repos/temporary-branches/"

[paths.tmp]
tmp_path = "{tmp_base_path}/doc-example-com"
"""
    configfile = tmp_path / "invalid-env.toml"
    configfile.write_text(content)
    context = DocBuildContext()
    result = runner.invoke(env, ["--config", str(configfile)], obj=context)
    assert result.exit_code != 0
    assert "ERROR: Invalid config file" in result.output
    assert context.configfile is None


def test_showconfig_env_role_option(runner, tmp_path):
    content = """# Test file
[paths]
config_dir = "/etc/docbuild"
repo_dir = "/data/docserv/repos/permanent-full/"
temp_repo_dir = "/data/docserv/repos/temporary-branches/"

[paths.tmp]
tmp_base_path = "/tmp"
tmp_path = "{tmp_base_path}/doc-example-com"
"""
    envfile = ENV_CONFIG_FILENAME.format(role="production")
    configfile = tmp_path / envfile
    configfile.write_text(content)

    with chdir(tmp_path):
        context = DocBuildContext()
        result = runner.invoke(env, ["--role", "production"], obj=context)

    assert result.exit_code == 0
    assert "tmp_path" in result.output
    assert context.configfile == Path(envfile)


def test_env_no_config_no_role(runner):
    context = DocBuildContext()

    # invoke without --role and --config
    result = runner.invoke(env, [], obj=context)

    assert result.exit_code != 0

    # Also check output message or exception type
    assert "Error: Either --config or --role is required" in result.output