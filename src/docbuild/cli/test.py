"""
A test command
"""
import click

from .context import DocBuildContext


@click.command(
    name="test",
    hidden=True,
    help=__doc__,
    context_settings=dict(ignore_unknown_options=True),
)
@click.pass_context
def test(ctx):
    """test subcommand"""
    ctx.ensure_object(DocBuildContext)
    click.echo(ctx.obj)
    return ctx