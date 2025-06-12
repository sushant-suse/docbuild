import pytest

from docbuild.cli.cmd_cli import cli


@pytest.mark.skip('Replace --role with --env-config')
def test_c14n_command(fake_envfile, runner):
    result = runner.invoke(cli, ['--role=production', 'c14n'])
    assert result.exit_code == 0
