from pathlib import Path

# import tomlkit as toml
import tomllib as toml

from ..constants import ENV_CONFIG_FILENAME, SERVER_GROUP_ROLES, SERVER_ROLES


def load_env_config(*paths: str | Path, role: str ) -> dict:
    """Load a TOML configuration file for a specific server role
    from a list of directories.

    The function looks for a config file named using a role-specific placeholder in
    the `ENV_CONFIG_FILENAME` format, such as "config.production.toml". It searches
    variations of the role in order of priority within each role group.

    :param paths: One or more directory paths to search.
    :param role: The role name to use for configuration
                 (e.g., "prod", "stage", "test").
    :returns: The loaded TOML configuration.
    :raises ValueError: If the role is unknown.
    :raises FileNotFoundError: If no matching config file is found in the provided paths.
    """

    # Search paths for each variant of the role
    for variant in SERVER_ROLES: ## TODO: fix that
        filename = ENV_CONFIG_FILENAME.format(role=variant)
        for path in paths:
            config_path = Path(path) / filename
            if config_path.is_file():
                with config_path.open("rb") as f:
                    return toml.load(f)

    raise FileNotFoundError(f"No config file found for role {role!r} in paths: {paths}")

