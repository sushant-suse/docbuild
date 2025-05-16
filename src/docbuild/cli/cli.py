from pathlib import Path
from typing import cast

import click

from ..__about__ import __version__
from ..config.app import load_app_config
from ..constants import SERVER_ROLES
from .context import DocBuildContext
from .build import build
from .c14n import c14n
from .showconfig import showconfig
from .test import test


@click.group(
    name="docbuild",
    context_settings=dict(show_default=True,
                          help_option_names=["-h", "--help"]
                          ),
    help="Main CLI tool for document operations.",
)
@click.version_option(__version__,
                      # package_name=,
                      prog_name=__package__)
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.option(
    "--config",
    # Convert a click.Path -> pathlib.Path object via path_type:
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to the config file.",
)
@click.option(
    "-r",
    "--role",
    type=click.Choice(
        SERVER_ROLES,
        case_sensitive=False,
    ),
    # required=True,
    default="production",
    help="Set the role or the server",
)
@click.option("--dry-run",
    is_flag=True,
    help="Run without making changes")
@click.option("--debug/--no-debug", default=False, envvar="DOCBUILD_DEBUG")
@click.pass_context
def cli(ctx,
        verbose,
        config: Path,
        role,
        dry_run,
        debug
):
    ctx.ensure_object(DocBuildContext)
    # config:Path = cast(Path, config)
    cfg = load_app_config(config) if config is not None else load_app_config()
    ctx.obj = DocBuildContext(
        verbosity=verbose,
        configfile=str(config),
        config=cfg,
        role=role,
        dry_run=dry_run,
        debug=debug,
    )


cli.add_command(build)
cli.add_command(c14n)
cli.add_command(test)
cli.add_command(showconfig)


if __name__ == "__main__":
    cli()