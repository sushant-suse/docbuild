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
    click.secho(f"# ENV Config file '{ctx.obj.envconfigfiles}'", fg="blue")
    print(Pretty(ctx.obj.envconfig, expand_all=True))
