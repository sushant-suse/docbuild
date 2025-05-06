import click

from ..__about__ import __version__
from ..constants import SERVER_ROLE
from .context import DocBuildContext
from .build import build
from .c14n import c14n

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
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the config file.",
)
@click.option(
    "-r",
    "--role",
    type=click.Choice(
        SERVER_ROLE,
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
        config,
        role,
        dry_run,
        debug
):
    # ctx.max_content_width = 0  # Disable automatic line wrapping
    ctx.obj = DocBuildContext(
        verbosity=verbose,
        config=config,
        role=role,
        dry_run=dry_run,
        )


cli.add_command(build)
cli.add_command(c14n)


if __name__ == "__main__":
    cli()