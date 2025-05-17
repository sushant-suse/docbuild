from docbuild.cli.cli import cli
from docbuild.__about__ import __version__


def test_version_option(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output