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
    Replace placeholder values in a nested dictionary structure, e.g., from a TOML config.

    - `{foo}` resolves from the current section.
    - `{a.b.c}` resolves deeply from the config.
    - `{{foo}}` escapes to literal `{foo}`.

    :param config: The loaded configuration dictionary.
    :return: A new dictionary with placeholders replaced.
    :raises KeyError: If a placeholder cannot be resolved.
    """

    def lookup_placeholder(
        path: str, context: dict[str, Any], container_name: str
    ) -> Any:
        parts = path.split(".")
        value: Any = context
        resolved_path = []

        for part in parts:
            resolved_path.append(part)
            if not isinstance(value, dict):
                full_path = ".".join(resolved_path)
                raise KeyError(
                    f"While resolving '{{{path}}}' in '{container_name}': "
                    f"'{full_path}' is not a dictionary (got type {type(value).__name__})."
                )
            if part not in value:
                full_path = ".".join(resolved_path)
                raise KeyError(
                    f"While resolving '{{{path}}}' in '{container_name}': "
                    f"missing key '{part}' in path '{full_path}'."
                )
            value = value[part]

        return value

    def replacement(match: re.Match, container: Container, key: str | int) -> str:
        inner = match.group(1)
        container_name = (
            str(key) if isinstance(key, str) else f"list item at index {key}"
        )

        if "." in inner:
            return str(lookup_placeholder(inner, config, container_name))
        elif isinstance(container, dict) and inner in container:
            return str(container[inner])
        else:
            raise KeyError(
                f"While resolving '{{{inner}}}' in '{container_name}': "
                f"key '{inner}' not found in current section."
            )

    stack: list[StackItem] = [(config, key, config) for key in config]

    while stack:
        container, key, context = stack.pop()
        value = container[key]  # type: ignore[assignment]

        if isinstance(value, str):
            new_value = PLACEHOLDER_PATTERN.sub(
                lambda m: replacement(m, container, key), value
            )
            # The following two if statements are needed to avoid
            # VSCode errors in the IDE, but they are not necessary
            # for the code to work.
            if isinstance(container, dict) and isinstance(key, str):
                container[key] = new_value
            elif isinstance(container, list) and isinstance(key, int):
                container[key] = new_value

        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, (dict, list, str)):
                    stack.append((value, i, context))

        elif isinstance(value, dict):
            for subkey in value:
                stack.append((value, subkey, value))

        # else: primitive type → nothing to do

    return config
