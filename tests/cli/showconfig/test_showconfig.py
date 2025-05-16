from pathlib import Path

import pytest
from click.testing import CliRunner
from docbuild.cli.cli import cli


def test_showconfig_help_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["showconfig", "--help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "env" in result.output
