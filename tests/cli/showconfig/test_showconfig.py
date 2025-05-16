from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import click
from click.testing import CliRunner
from docbuild.cli.cli import cli
from docbuild.cli.showconfig import showconfig
from docbuild.cli.context import DocBuildContext


def test_showconfig_help_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["showconfig", "--help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "env" in result.output


def _test_showconfig_calls_ensure_object():

    @click.command()
    @click.pass_context
    def fake_showconfig(ctx, *args, **kwargs):
        mock_ctx = MagicMock()
        mock_ctx.ensure_object = MagicMock()
        result = showconfig(mock_ctx)
        ctx.obj = mock_ctx  # store mock on real ctx so we can access after invoke
        return result

    runner = CliRunner()
    with patch("click.Context.ensure_object") as mock_ensure_object:

        result = runner.invoke(showconfig, [], standalone_mode=False)
        # ensure command ran successfully
        assert result.exit_code == 0

        # mock_ctx = result.ctx.obj
        mock_ensure_object.assert_called_once_with(DocBuildContext)


def test_showconfig_calls_ensure_object():
    runner = CliRunner()

    # Wrapper function to spy on ctx.ensure_object
    @click.group()
    @click.pass_context
    def spy_showconfig(ctx):
        ctx.ensure_object = MagicMock(wraps=ctx.ensure_object)
        showconfig(ctx)
        ctx.ensure_object.assert_called_once_with(DocBuildContext)

    result = runner.invoke(spy_showconfig, [])
    assert result.exit_code == 0