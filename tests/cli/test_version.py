from docbuild.__about__ import __version__
from docbuild.cli.cli import cli


def test_version_option(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output
