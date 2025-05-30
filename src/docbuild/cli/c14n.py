"""Apply canonicals."""

import click

from .context import DocBuildContext


@click.command(help=__doc__)
@click.pass_context
def c14n(ctx: click.Context) -> None:
    """Subcommand c14n."""
    ctx.ensure_object(DocBuildContext)
    context: DocBuildContext = ctx.obj
    click.echo(f"[C17N] Verbosity: {context.verbose}")
