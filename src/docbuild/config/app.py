from pathlib import Path
import re
from typing import Any

# import tomlkit as toml
import tomllib as toml

from ..constants import (
    APP_CONFIG_PATHS,
    APP_CONFIG_FILENAME,
    PLACEHOLDER_PATTERN
)
from .merge import deep_merge


# Type aliases
Container = dict[str, Any] | list[Any]
StackItem = tuple[Container, str | int, Container]


def load_app_config(
    *paths: str | Path, default: tuple[str | Path, ...] = APP_CONFIG_PATHS
) -> dict:
    """Load the app's config files and merge all content regardless
    of the nesting level

    :param paths: the paths to look for config files
    :param default: the default paths to use, when `paths` are empty.
    :return: the merged dictionary
    """
    configs = []
    if not paths:
        paths = default
    for path in paths:
        path = Path(path).expanduser().resolve() / APP_CONFIG_FILENAME

        if path.exists():
            with path.open("rb") as f:
                configs.append(toml.load(f))
        else:
            configs.append({})  # fallback empty

    return deep_merge(*configs)


def replace_placeholders(config: dict[str, Any]) -> dict[str, Any]:
    """
    Replace placeholder values in the configuration dictionary.

    Placeholders are indicated by `{placeholder}` syntax. If the name contains dots,
    it is treated as a reference to a nested section, e.g. `{server.name}`. If no dot
    is present, it looks up the value in the current section.

    Double curly braces like `{{foo}}` are treated as escaped and returned as `{foo}`.

    :param config: The loaded TOML configuration as a dictionary.
    :return: A new dictionary with all placeholders replaced.
    :raises KeyError: If a placeholder cannot be resolved.
    """

    def lookup_placeholder(path: str, context: dict[str, Any]) -> Any:
        parts = path.split(".")
        value: Any = context
        for part in parts:
            if not isinstance(value, dict):
                raise KeyError(
                    f"Cannot resolve '{path}': '{part}' is not a dictionary."
                )
            if part not in value:
                raise KeyError(f"Cannot resolve placeholder: '{path}'")
            value = value[part]
        return value

    stack: list[StackItem] = [(config, key, config) for key in config]

    while stack:
        container, key, context = stack.pop()
        value = container[key] # type: ignore

        if isinstance(value, str):

            def replacement(match: re.Match) -> str:
                inner = match.group(1)
                if "." in inner:
                    return str(lookup_placeholder(inner, config))
                elif isinstance(container, dict) and inner in container:
                    return str(container[inner])
                else:
                    raise KeyError(f"Cannot resolve placeholder: '{inner}'")

            new_value = PLACEHOLDER_PATTERN.sub(replacement, value)
            container[key] = new_value  # type: ignore

        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, (dict, list, str)):
                    stack.append((value, i, context))

        elif isinstance(value, dict):
            for subkey in value:
                stack.append((value, subkey, value))

        # else: keep literal value (int, bool, etc.)

    return config
