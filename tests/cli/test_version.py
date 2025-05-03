from click.testing import CliRunner
from docbuild.cli import cli


def test_version_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "Version:" in result.output