"""Main CLI tool for document operations."""

from pathlib import Path

import click
from click_option_group import MutuallyExclusiveOptionGroup, optgroup

from ..__about__ import __version__
from ..config.load import load_and_merge_configs, process_envconfig_and_role
from ..constants import (
    APP_CONFIG_FILENAME,
    CONFIG_PATHS,
    DEFAULT_ENV_CONFIG_FILENAME,
    ENV_CONFIG_FILENAME,
    SERVER_ROLES,
    SHARE_ENV_CONFIG_FILENAME,
)
from ..models.env.serverroles import ServerRole
from .build import build
from .c14n import c14n
from .context import DocBuildContext
from .showconfig import showconfig


class DocbuildGroup(click.Group):
    """Custom click group to handle the docbuild CLI commands."""

    def invoke(self, ctx: click.Context):  # noqa: ANN201
        """Override the invoke method to handle command-line options."""
        # click.echo(
        #      f"DocbuildGroup.invoke: {ctx=} {ctx.parent=} "
        #      f"{ctx.invoked_subcommand=} {ctx.args=} "
        #      f"{ctx.obj=}"
        # )
        help_flags = {"--help", "-h"}
        if not any(flag in ctx.args for flag in help_flags):
            role = ctx.params.get("role")
            env_config = ctx.params.get("env_config")
            if not role and not env_config:
                    raise click.UsageError(
                         "Must provide one of: --role or --env-config",
                    )
            if role and env_config:
                raise click.UsageError(
                         "--role and --env-config are mutually exclusive",
                    )

            # Ensure ctx.obj exists
            context = ctx.ensure_object(DocBuildContext)
            # Store global options
            context.debug = ctx.params.get("debug", False)
            context.dry_run = ctx.params.get("dry_run", False)
            context.verbose = ctx.params.get("verbose", 0)

            # Store values on the context object for downstream use
            if role:
                context.role = ServerRole[role]
                context.envconfigfiles = (DEFAULT_ENV_CONFIG_FILENAME,)
            if env_config:
                context.envconfigfiles = (env_config,)
            print(f"DocbuildGroup.invoke: {context=}")

        return super().invoke(ctx)


@click.group(
    name="docbuild",
    cls=DocbuildGroup,
    context_settings=dict(show_default=True, help_option_names=["-h", "--help"]),
    help="Main CLI tool for document operations.",
)
@click.version_option(__version__,
                      # package_name=,
                      prog_name=__package__)
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@optgroup.group(
    "Configuration options",
    cls=MutuallyExclusiveOptionGroup,
    help="Select server role or directly the env configuration file.",
)
@optgroup.option("--env-config", # "envfile",
    metavar="ENV_CONFIG",
    type=click.Path(exists=True, dir_okay=False),
    # required=True,
    # default=None,
    help=(
        "Path to a single ENV config file. "
        "Will only load this file, no shared config files."
        ),
)
@optgroup.option("--role",
    type=click.Choice(
        SERVER_ROLES,
        case_sensitive=False,
    ),
    help=("Set the role or the server. "
          f"Will load the shared config file {SHARE_ENV_CONFIG_FILENAME} first "
          "and then the ENV config file "
          f"{ENV_CONFIG_FILENAME!r}. "
          ),
)
@click.option("--dry-run",
    is_flag=True,
    help="Run without making changes")
@click.option(
    "--debug/--no-debug",
    default=False,
    envvar="DOCBUILD_DEBUG",
    help=(
        "Enable debug mode. "
        "This will show more information about the process and the config files. "
        "If available, read the environment variable 'DOCBUILD_DEBUG'."
    ),
)
# @pass_docbuild
@click.pass_context
def cli(ctx: click.Context,
        verbose: int,
        env_config: Path,
        role: str,
        dry_run: bool,
        debug: bool,
) -> None:
    """Acts as a main entry point for CLI tool."""
    # ctx.ensure_object(DocBuildContext)
    if ctx.obj is None:
        click.echo("Creating new DocBuildContext object")
        ctx.ensure_object(DocBuildContext)
    context = ctx.obj
    # click.echo(f"\ncli:type of ctx: {type(ctx)=}, {ctx=}")
    # click.echo(f"  obj: {context=}")
    # click.echo(f"cli: {ctx.invoked_subcommand}")
    # click.echo(f"  {ctx.parent=}")
    # click.echo(f"  {ctx.args=}")
    # click.echo(f"  {ctx.command=}")
    # click.echo(f"  {context.role=}, {context.envconfigfiles=}")
    # click.echo(f"  > {verbose=}, {env_config=}, {role=}, {dry_run=}, {debug=}")

    # Load the app's config files
    cfgfiles, cfg = load_and_merge_configs([APP_CONFIG_FILENAME], *CONFIG_PATHS)
    # Load the env config file and process it
    envfile, envconfig = process_envconfig_and_role(env_config, role=role)

    # We don't create a new object, but use the existing one
    context.verbose = verbose
    context.appconfigfiles=cfgfiles
    context.appconfig=cfg
    context.dry_run=dry_run
    context.debug=debug
    context.role = ServerRole[role] if role else None
    context.envconfigfiles = (Path(envfile.absolute()),)
    context.envconfig = envconfig


cli.add_command(build)
cli.add_command(c14n)
cli.add_command(showconfig)


if __name__ == "__main__":
    cli()
