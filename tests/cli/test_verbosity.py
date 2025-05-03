from click.testing import CliRunner
from docbuild.cli import cli

def test_verbosity_counts(monkeypatch):
    runner = CliRunner()
    # role is required, so add it
    result = runner.invoke(cli, ["-vvv"])
    assert result.exit_code == 0
    assert "Verbosity level: 3" in result.output
    print(">>>", dir(result))