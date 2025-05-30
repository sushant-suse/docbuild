from docbuild.cli.cli import cli

from ..common import changedir


def test_c14n_command(fake_envfile, runner):
    result = runner.invoke(cli, ["--role=production", "c14n"])
    assert result.exit_code == 0
