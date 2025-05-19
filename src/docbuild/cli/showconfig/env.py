"""Shows the configuration of the application.
"""

from pathlib import Path
import tomllib as toml

import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup

from rich import print
from rich.pretty import Pretty


@click.command(
    help=__doc__
)
@click.pass_context
def env(ctx,):
    """Show the ENV configuration."""

    click.secho(f"# ENV Config file '{ctx.obj.envconfigfiles}'", fg="blue")
    print(Pretty(ctx.obj.envconfig, expand_all=True))
    # print(">>>", ctx.obj)
