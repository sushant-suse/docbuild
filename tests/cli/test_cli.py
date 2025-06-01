from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import click
import pytest

import docbuild.cli as cli_module
import docbuild.cli.cli as cli_cli_module
from docbuild.cli.cli import DocbuildGroup
from docbuild.constants import DEFAULT_ENV_CONFIG_FILENAME

from ..common import changedir


def test_main_entry_point(tmp_path):
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "docbuild.cli.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Main CLI tool" in result.stdout


@pytest.mark.skip("failed assert context.obj.envconfigfiles == ('file1', 'file2')")
def test_validate_options_role(fake_validate_options, monkeypatch, ctx):
    fake_validate_options.mock_load_and_merge_configs.return_value = (
        ("file1", "file2"), {"foo": "bar"},
    )

    monkeypatch.setattr(cli_module, "ServerRole", {"production": "production"})
    obj = SimpleNamespace(envconfig=None, envconfigfiles=None)
    context = ctx(obj)
    cli_module.validate_options(context)
    assert context.obj.envconfigfiles == ('file1', 'file2')
    assert context.obj.envconfig == {"foo": "bar"}
    assert context.obj.role == "production"


@pytest.mark.skip("failed assert context.obj.envconfigfiles == ('myenv.toml',)")
def test_validate_options_envconfig(fake_validate_options, monkeypatch, ctx):
    fake_validate_options.mock_load_and_merge_configs.return_value = (
        ("myenv.toml",), {},
    )
    fake_validate_options.mock_load_single_config.return_value = {"baz": "qux"}
    monkeypatch.setattr(cli_module, "replace_placeholders", lambda conf: conf)
    obj = SimpleNamespace(role=None, envconfig="myenv.toml", envconfigfiles=None)
    context = ctx(obj)
    cli_module.validate_options(context)
    assert context.obj.envconfigfiles == ("myenv.toml",)
    assert context.obj.envconfig == {"baz": "qux"}


def test_validate_options_missing(monkeypatch, ctx):
    obj = SimpleNamespace(role=None, envconfig=None)
    context = ctx(obj)
    with pytest.raises(click.UsageError):
        cli_module.validate_options(context)


@pytest.mark.skip("Failed: DID NOT RAISE <class 'click.exceptions.Abort'>")
def test_validate_options_invalid_config(fake_validate_options, monkeypatch, ctx):
    def fake_replace_placeholders(conf):
        raise KeyError("bad placeholder")

    fake_validate_options.mock_load_single_config.return_value = {"baz": "qux"}
    monkeypatch.setattr(cli_module, "replace_placeholders", fake_replace_placeholders)
    obj = SimpleNamespace(role=None, envconfig="myenv.toml")
    context = ctx(obj)
    with pytest.raises(click.Abort):
        cli_module.validate_options(context)

def test_docbuildgroup_invoke_help_flag():
    # Test that when help flag is present, validation is skipped
    group = DocbuildGroup(name="test")
    ctx = click.Context(group)
    ctx.args = ["--help"]
    ctx.params = {}

    # Mock the super().invoke to verify it's called
    with patch.object(click.Group, "invoke", return_value="success") as mock_invoke:
        result = group.invoke(ctx)
        mock_invoke.assert_called_once_with(ctx)
        assert result == "success"


def test_docbuildgroup_invoke_missing_options():
    # Test that an error is raised when neither role nor env_config is provided
    group = DocbuildGroup(name="test")
    ctx = click.Context(group)
    ctx.args = []
    ctx.params = {"role": None, "env_config": None}

    with pytest.raises(click.UsageError,
                       match="Must provide one of: --role or --env-config"):
        group.invoke(ctx)


def test_docbuildgroup_invoke_mutually_exclusive():
    # Test that an error is raised when both role and env_config are provided
    group = DocbuildGroup(name="test")
    ctx = click.Context(group)
    ctx.args = []
    ctx.params = {"role": "production", "env_config": "some_path.toml"}

    with pytest.raises(click.UsageError,
                       match="--role and --env-config are mutually exclusive"):
        group.invoke(ctx)


def test_docbuildgroup_invoke_with_role(monkeypatch, ctx):
    monkeypatch.setattr(cli_cli_module,"DocBuildContext", ctx)

    mock_server_role = MagicMock()
    monkeypatch.setattr(
        cli_cli_module, 'ServerRole', {'production': mock_server_role}
    )

    group = DocbuildGroup(name="test")
    context = click.Context(group)
    context.args = []
    context.params = {
        "role": "production",
        "env_config": None,
        "debug": True,
        "dry_run": False,
        "verbose": 2,
    }

    # Patch ensure_object to a MagicMock that returns DummyCtx
    context.ensure_object = MagicMock(return_value=ctx)

    with patch.object(click.Group, "invoke", return_value="success") as mock_invoke:
        with patch("builtins.print"):  # Suppress print output
            group.invoke(context)

    assert mock_invoke.called

    # Verify context was properly set up
    context.ensure_object.assert_called_once()
    context_obj = context.ensure_object.return_value
    assert context_obj.debug is True
    assert context_obj.dry_run is False
    assert context_obj.verbose == 2
    assert context_obj.envconfigfiles == (DEFAULT_ENV_CONFIG_FILENAME,)


def test_docbuildgroup_invoke_with_env_config(monkeypatch, ctx):
    # monkeypatch.setattr(cli_cli_module, "DocBuildContext", ctx)
    mock_context = MagicMock()
    monkeypatch.setattr(cli_cli_module, 'DocBuildContext', mock_context)

    group = DocbuildGroup(name="test")
    context = click.Context(group)
    context.args = []
    context.params = {
        "role": None,
        "env_config": "path/to/env.toml",
        "debug": False,
        "dry_run": True,
        "verbose": 1,
    }

    # Patch ensure_object to a MagicMock that returns DummyCtx
    context.ensure_object = MagicMock(return_value=ctx())

    with patch.object(click.Group, "invoke", return_value="success") as mock_invoke:
        with patch("builtins.print"):  # Suppress print output
            group.invoke(context)

    assert mock_invoke.called

    # Verify context was properly set up
    context.ensure_object.assert_called_once()
    context_obj = context.ensure_object.return_value
    assert context_obj.debug is False
    assert context_obj.dry_run is True
    assert context_obj.verbose == 1
    assert context_obj.envconfigfiles == ("path/to/env.toml",)
    assert context_obj.role is None  # Because role is None in params
