"""Shows config files how docbuild sees it."""

import click

from .application import app
from .environment import env


@click.group(
    name="config",
    help=__doc__,
)
@click.pass_context
def config(ctx: click.Context) -> None:
    """Show the configuration files and their content."""
    pass


# Register the subcommands for the config group
config.add_command(env)
config.add_command(app)
