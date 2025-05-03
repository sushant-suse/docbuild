import click
from .context import DocBuildContext


@click.command()
@click.pass_context
def c14n(ctx):
    context: DocBuildContext = ctx.obj
    click.echo(f"[C17N] Verbosity: {context.verbosity}")
