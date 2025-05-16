"""Shows config files how docbuild sees it.
"""

import click

from .env import env
from ...cli.context import DocBuildContext

@click.group(
    name="showconfig",
    help=__doc__,
)
@click.pass_context
def showconfig(ctx):
    # print(">> ensure_object from:", ctx.ensure_object.__module__)
    ctx.ensure_object(DocBuildContext)


showconfig.add_command(env)