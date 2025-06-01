from unittest.mock import MagicMock

from docbuild.cli.cli import cli
from docbuild.cli.config import config
from docbuild.cli.context import DocBuildContext


def test_showconfig_help_option(runner):
    result = runner.invoke(cli, ["config", "--help"])
    print(result.output)
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "env" in result.output
