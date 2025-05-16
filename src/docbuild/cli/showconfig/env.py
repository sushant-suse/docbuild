"""Shows the configuration of the application.
"""

from pathlib import Path
import tomllib as toml

import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup

from rich import print
from rich.pretty import Pretty

from ...config.app import replace_placeholders
from ...constants import ENV_CONFIG_FILENAME, SERVER_ROLES
from ...cli.context import DocBuildContext

@click.command(
    help=__doc__
)
@optgroup.group(
    "Configuration options",
    cls=MutuallyExclusiveOptionGroup,
    help="Select server role or directly the env configuration file.",
)
@optgroup.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to the config file.",
)
@optgroup.option(
    "--role",
    type=click.Choice(
        SERVER_ROLES,
        case_sensitive=False,
    ),
    help="Set the role or the server",
)
@click.pass_context
def env(ctx, config: Path, role: str):
    """Show the ENV configuration."""
    ctx.ensure_object(DocBuildContext)

    if role:
        config = Path(ENV_CONFIG_FILENAME.format(role=role))
        # click.echo(f">> {config=}")
    elif config:
        config = Path(config)
    else:
        raise click.UsageError("Either --config or --role is required.")

    try:
        with config.open("rb") as f:
            ctx.obj.rawconfig = toml.load(f)
            ctx.obj.config = replace_placeholders(ctx.obj.rawconfig)
    except KeyError as e:
        click.secho(
            f"ERROR: Invalid config file: {e}",
            fg="red",
            err=True,
        )
        raise click.Abort()

    ctx.obj.configfile = config
    click.secho(f"# Config file '{config}'", fg="blue")

    print(Pretty(ctx.obj.config, expand_all=True))
