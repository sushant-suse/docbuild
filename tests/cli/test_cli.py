from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import click
import pytest

from docbuild.cli import validate_options
from docbuild.cli.cli import DocbuildGroup
from docbuild.constants import DEFAULT_ENV_CONFIG_FILENAME


class DummyContext:
    def __init__(self, *a, **kw):
        self.debug = None
        self.dry_run = None
        self.verbose = None
        self.envconfigfiles = None
        self.role = None


def test_main_entry_point(tmp_path):
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "docbuild.cli.cli", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
    assert "Main CLI tool" in result.stdout


def test_validate_options_role(monkeypatch, ctx):
    # Mock config loading
    monkeypatch.setattr(
        "docbuild.cli.load_and_merge_configs",
        lambda *a, **kw: (["file1", "file2"], {"foo": "bar"}),
    )
    monkeypatch.setattr("docbuild.cli.ServerRole", {"production": "production"})
    obj = SimpleNamespace(role="production", envconfig=None)
    context = ctx(obj)
    validate_options(context)
    assert context.obj.envconfigfiles == ["file1", "file2"]
    assert context.obj.envconfig == {"foo": "bar"}
    assert context.obj.role == "production"


def test_validate_options_envconfig(monkeypatch, ctx):
    monkeypatch.setattr("docbuild.cli.load_single_config", lambda path: {"baz": "qux"})
    monkeypatch.setattr("docbuild.cli.replace_placeholders", lambda conf: conf)
    obj = SimpleNamespace(role=None, envconfig="myenv.toml")
    context = ctx(obj)
    validate_options(context)
    assert context.obj.envconfigfiles == ("myenv.toml",)
    assert context.obj.envconfig == {"baz": "qux"}


def test_validate_options_missing(monkeypatch, ctx):
    obj = SimpleNamespace(role=None, envconfig=None)
    context = ctx(obj)
    with pytest.raises(click.UsageError):
        validate_options(context)


def test_validate_options_invalid_config(monkeypatch, ctx):
    def fake_replace_placeholders(conf):
        raise KeyError("bad placeholder")

    monkeypatch.setattr("docbuild.cli.load_single_config", lambda path: {"baz": "qux"})
    monkeypatch.setattr("docbuild.cli.replace_placeholders", fake_replace_placeholders)
    obj = SimpleNamespace(role=None, envconfig="myenv.toml")
    context = ctx(obj)
    with pytest.raises(click.Abort):
        validate_options(context)

def test_docbuildgroup_invoke_help_flag(monkeypatch):
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


def test_docbuildgroup_invoke_with_role(monkeypatch):
    monkeypatch.setattr("docbuild.cli.cli.DocBuildContext", DummyContext)

    mock_server_role = MagicMock()
    monkeypatch.setattr("docbuild.cli.cli.ServerRole", {"production": mock_server_role})

    group = DocbuildGroup(name="test")
    ctx = click.Context(group)
    ctx.args = []
    ctx.params = {
        "role": "production",
        "env_config": None,
        "debug": True,
        "dry_run": False,
        "verbose": 2,
    }

    # Patch ensure_object to a MagicMock that returns DummyContext
    ctx.ensure_object = MagicMock(return_value=DummyContext())

    with patch.object(click.Group, "invoke", return_value="success") as mock_invoke:
        with patch("builtins.print"):  # Suppress print output
            group.invoke(ctx)

    assert mock_invoke.called

    # Verify context was properly set up
    ctx.ensure_object.assert_called_once()
    context_obj = ctx.ensure_object.return_value
    assert context_obj.debug is True
    assert context_obj.dry_run is False
    assert context_obj.verbose == 2
    assert context_obj.envconfigfiles == (DEFAULT_ENV_CONFIG_FILENAME,)


def test_docbuildgroup_invoke_with_env_config(monkeypatch):

    monkeypatch.setattr("docbuild.cli.cli.DocBuildContext", DummyContext)

    mock_context = MagicMock()
    monkeypatch.setattr("docbuild.cli.cli.DocBuildContext", mock_context)

    group = DocbuildGroup(name="test")
    ctx = click.Context(group)
    ctx.args = []
    ctx.params = {
        "role": None,
        "env_config": "path/to/env.toml",
        "debug": False,
        "dry_run": True,
        "verbose": 1,
    }

    # Patch ensure_object to a MagicMock that returns DummyContext
    ctx.ensure_object = MagicMock(return_value=DummyContext())

    with patch.object(click.Group, "invoke", return_value="success") as mock_invoke:
        with patch("builtins.print"):  # Suppress print output
            group.invoke(ctx)

    assert mock_invoke.called

    # Verify context was properly set up
    ctx.ensure_object.assert_called_once()
    context_obj = ctx.ensure_object.return_value
    assert context_obj.debug is False
    assert context_obj.dry_run is True
    assert context_obj.verbose == 1
    assert context_obj.envconfigfiles == ("path/to/env.toml",)
    assert context_obj.role is None  # Because role is None in params
