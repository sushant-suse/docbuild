
from click.testing import CliRunner

import pytest

from docbuild.cli.cli import cli


def test_c14n_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["c14n"])
    assert result.exit_code == 0