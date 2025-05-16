"""Shows config files how docbuild sees it.
"""

import click

from .env import env


@click.group(
    name="showconfig",
    help=__doc__,
)
@click.pass_context
def showconfig(ctx, ):
    pass


showconfig.add_command(env)