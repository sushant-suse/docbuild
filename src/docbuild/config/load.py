from collections.abc import Sequence
from itertools import product
from pathlib import Path
import tomllib as toml
from typing import Any

import click

from .app import Container, replace_placeholders
from .merge import deep_merge
from ..constants import DEFAULT_ENV_CONFIG_FILENAME, ENV_CONFIG_FILENAME
from ..models.env.serverroles import ServerRole


def process_envconfig_and_role(
    envconfigfile: Path | None, role: str | None
) -> tuple[Path, Container]:
    """Process the env config and role options.

    :param envconfigfile: Path to the env config file.
    :param role: Role of the server.
    :return: Tuple of the env config file path and the config object.
    :raise ValueError: If neither envconfigfile nor role is provided.
    """
    if role:
        # Normalize the role with the ServerRole enum:
        serverrole = ServerRole[role]
        envconfigfile = Path(ENV_CONFIG_FILENAME.format(role=serverrole.value))
    elif envconfigfile:
        envconfigfile = Path(envconfigfile)
    else:
        # If we don't have a role nor a envconfigfile, we need to find the default one.
        # We will look for the default env config file in the current directory.

        if (rfile := Path(DEFAULT_ENV_CONFIG_FILENAME)).exists():
            envconfigfile = rfile
            click.echo(f"Using env config file: {envconfigfile}")
        else:
            raise click.UsageError(
                f"Could not find default ENV configuration file {rfile}."
            )

    with envconfigfile.open("rb") as f:
        rawconfig = toml.load(f)
        # ctx.obj.envconfig = replace_placeholders(rawconfig)

    return envconfigfile, replace_placeholders(rawconfig)


def load_single_config(configfile: str | Path) -> dict[str, Any]:
    """Load a single config file and return its content.

    :param configfile: Path to the config file.
    :return: The loaded config as a dictionary.
    """
    with Path(configfile).open("rb") as f:
        return toml.load(f)


def load_and_merge_configs(defaults: Sequence[str | Path], *paths: str | Path,
) -> tuple[tuple[str | Path, ...], dict[str, Any]]:
    """Load the app's config files and merge all content regardless
    of the nesting level

    The order of defaults and paths is important. The paths are in the order of
    system path, user path, and current working directory.
    The defaults are in the order of common config file names followed by more
    specific ones.

    :param defaults: a sequence of base filenames (without path!) to look for in the paths
    :param paths: the paths to look for config files (without the filename!)
    :return: the found config files and the merged dictionary
    """
    configs: Sequence[dict[str, Any]] = []
    configfiles: Sequence[Path] = []

    # If no paths are provided, raise an error:
    if not paths:
        raise ValueError(
            "No paths provided. Please provide at least one path to load the config files."
        )

    # Create a carthesian product of paths and default filenames:
    for path, cfgfile in product(paths, defaults):
        path = Path(path).expanduser().resolve() / cfgfile

        if path.exists():
            configfiles.append(path)
            configs.append(load_single_config(path))
        # Silently ignore files that do not exist:

    return tuple(configfiles), deep_merge(*configs)
