from pathlib import Path
from unittest.mock import ANY, call, MagicMock

import pytest
import click
import click.testing

from docbuild.cli.cli import cli
from docbuild.cli.context import DocBuildContext

from ...common import changedir


# Define a throwaway command just for testing context mutation
@cli.command('capture-context')
@click.pass_context
def capture_context(ctx):
    """
    Dummy command that simulates work and stores final context
    for inspection in testing.
    """
    # We don't echo anything; we only mutate the context
    # click.echo(ctx.obj)
    pass

# Register the test-only command temporarily
cli.add_command(capture_context)



def test_showconfig_env_help_option(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "[mutually_exclusive]" in result.output
    assert "--env-config" in result.output
    assert "--role" in result.output


def test_showconfig_env_config_option(runner):
    configfile = Path(__file__).parent / "sample-env.toml"
    context = DocBuildContext()
    result = runner.invoke(
        cli,
        [
            "--env-config", str(configfile),
            "showconfig", "env",
        ],
        obj=context
    )
    assert result.exit_code == 0
    # assert "# ENV Config file " in result.output
    assert context.envconfigfiles == (configfile,)


def test_showconfig_env_config_option_invalidfile(runner, tmp_path):
    content = """
[paths]
config_dir = "/etc/docbuild"
repo_dir = "/data/docserv/repos/permanent-full/"
temp_repo_dir = "/data/docserv/repos/temporary-branches/"

[paths.tmp]
tmp_path = "{tmp_base_path}/doc-example-com"
"""
    configfile = tmp_path / "invalid-env.toml"
    configfile.write_text(content)
    context = DocBuildContext()

    with changedir(tmp_path):
        result = runner.invoke(
            cli,
            ["--env-config", str(configfile), "showconfig", "env"],
            obj=context
        )
    assert result.exit_code != 0
    # assert "ERROR: Invalid config file" in result.output



def test_showconfig_env_role_option(
    monkeypatch, runner,
):
    fakefile = Path("fake_envfile")
    # Mock the config/environment loader to avoid file I/O
    def fake_process_envconfig_and_role(env_config, role=None):
        print("## fake_process_envconfig_and_role called with",)
        # Return whatever your CLI expects (envfile, envconfig)
        return fakefile, {
            "paths": {
                "config_dir": "/etc/docbuild",
                "repo_dir": "/data/docserv/repos/permanent-full/",
                "temp_repo_dir": "/data/docserv/repos/temporary-branches/",
                "tmp": {"tmp_base_path": "/tmp", "tmp_path": "/tmp/doc-example-com"},
            }
        }

    monkeypatch.setattr(
        "docbuild.cli.cli.process_envconfig_and_role", fake_process_envconfig_and_role
    )


    context = DocBuildContext()
    result = runner.invoke(
        cli,
        ["--role=production", "showconfig", "env"],
        obj=context
    )

    assert result.exit_code == 0
    assert context.envconfigfiles == (fakefile.absolute(),)
    print("## context.envconfigfiles:", context.envconfigfiles)
    assert context.envconfig == {
        "paths": {
            "config_dir": "/etc/docbuild",
            "repo_dir": "/data/docserv/repos/permanent-full/",
            "temp_repo_dir": "/data/docserv/repos/temporary-branches/",
            "tmp": {
                "tmp_base_path": "/tmp",
                "tmp_path": "/tmp/doc-example-com"
            }
        }
    }


def test_env_no_config_no_role(tmp_path, runner):
    context = DocBuildContext()

    with changedir(tmp_path):
        # invoke without --role and --config
        result = runner.invoke(
            cli, ["--role=production", "showconfig", "env"], obj=context
        )

    assert result.exit_code != 0
    assert isinstance(result.exception, FileNotFoundError)
    assert "No such file or directory" in str(result.exception)
