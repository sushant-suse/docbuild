"""Shows the configuration of the environment files."""


import click
from rich import print  # noqa: A004
from rich.pretty import Pretty


@click.command(
    help=__doc__,
)
@click.pass_context
def env(ctx: click.Context) -> None:
    """Show the ENV configuration."""
    path = ", ".join(str(path) for path in ctx.obj.envconfigfiles)
    click.secho(f"# ENV Config file '{path}'", fg="blue")
    print(Pretty(ctx.obj.envconfig, expand_all=True))
