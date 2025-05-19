from docbuild.cli.cli import cli

from ..common import changedir


def test_c14n_command(env_content, runner):
    tmp_path = env_content.parent
    with changedir(tmp_path):
        # Invoke the c14n command
        result = runner.invoke(cli, ["--role=production", "c14n"])
    assert result.exit_code == 0