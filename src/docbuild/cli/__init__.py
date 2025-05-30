"""docbuild - A tool for building documentation from source files."""

import click

from ..config.app import replace_placeholders
from ..config.load import load_and_merge_configs, load_single_config
from ..constants import CONFIG_PATHS, ENV_CONFIG_FILENAME, SHARE_ENV_CONFIG_FILENAME
from ..models.env.serverroles import ServerRole


def validate_options(ctx: click.Context) -> None:
    """Check for mutually exclusive options only when a command is executed."""
    if not (ctx.obj.role or ctx.obj.envconfig):
        raise click.UsageError("You must provide either --role or --env-config.")

    if ctx.obj.role:
        ctx.obj.envconfigfiles, ctx.obj.envconfig = load_and_merge_configs(
            [SHARE_ENV_CONFIG_FILENAME, ENV_CONFIG_FILENAME.format(role=ctx.obj.role)],
            *CONFIG_PATHS,
        )
        ctx.obj.role = ServerRole[ctx.obj.role]
    else:
        ctx.obj.envconfigfiles = (ctx.obj.envconfig,)
        ctx.obj.envconfig = load_single_config(ctx.obj.envconfig)
        try:
            ctx.obj.envconfig = replace_placeholders(ctx.obj.envconfig)  # type: ignore
        except KeyError as e:
            click.secho(
                f"ERROR: Invalid config file: {e}",
                fg="red",
                err=True,
            )
            raise click.Abort() from e
