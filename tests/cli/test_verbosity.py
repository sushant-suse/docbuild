import pytest

from docbuild.cli.cli import cli


@pytest.mark.skip("Need a complete (sub)command")
def test_verbosity_counts(runner):
    # role is required, so add it
    result = runner.invoke(cli, ["-vvv", "build"])
    assert result.exit_code == 2
    # assert "Verbosity level: 3" in result.output
    # print(">>>", result.return_value)
    # print(">>>", result.output)
