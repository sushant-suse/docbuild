from unittest.mock import MagicMock

import click

from docbuild.cli.cli import cli
from docbuild.cli.config import config
from docbuild.cli.context import DocBuildContext


def test_showconfig_help_option(runner):
    result = runner.invoke(cli, ["config", "--help"])
    print(result.output)
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "env" in result.output


def test_showconfig_calls_ensure_object(runner):

    # Wrapper function to spy on ctx.ensure_object
    @click.group()
    @click.pass_context
    def spy_showconfig(ctx) -> None:
        ctx.ensure_object = MagicMock(wraps=ctx.ensure_object)
        config(ctx)
        ctx.ensure_object.assert_called_once_with(DocBuildContext)

    result = runner.invoke(spy_showconfig, [])
    assert result.exit_code == 0
