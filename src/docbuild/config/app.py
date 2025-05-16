from collections.abc import Sequence
from pathlib import Path
import re
from typing import Any, TypedDict

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
# class StackItem(TypedDict):
#     container: Container
#     section_key: str
#     parent: Container | Sequence[Any] | None

#: Maximum recursion depth for placeholder replacement
MAX_RECURSION_DEPTH: int = 10


#: Maximum recursion depth for placeholder replacement
MAX_RECURSION_DEPTH: int = 10


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


def replace_placeholders(config: Container,
                         max_recursion_depth: int = MAX_RECURSION_DEPTH) -> Container:
    """
    Replace placeholder values in a nested dictionary structure, e.g., from a TOML config.

    - `{foo}` resolves from the current section.
    - `{a.b.c}` resolves deeply from the config.
    - `{{foo}}` escapes to literal `{foo}`.

    :param config: The loaded configuration dictionary.
    :return: A new dictionary with placeholders replaced.
    :raises KeyError: If a placeholder cannot be resolved.
    """

    def lookup_placeholder(path: str, context: dict[str, Any], container_name: str) -> Any:
        parts = path.split(".")
        value: Any = context
        resolved_path = []

        for part in parts:
            resolved_path.append(part)
            if not isinstance(value, dict):
                full_path = ".".join(resolved_path)
                raise KeyError(
                    f"While resolving '{{{path}}}' in '{container_name}': "
                    f"'{full_path}' is not a dictionary "
                    f"(got type {type(value).__name__})."
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
        container_name = str(key) if isinstance(key, str) else f"list item at index {key}"

        if "." in inner:
            return str(lookup_placeholder(inner, config, container_name))
        elif isinstance(container, dict) and inner in container:
            return str(container[inner])
        else:
            raise KeyError(
                f"While resolving '{{{inner}}}' in '{container_name}': key '{inner}' not found in current section."
            )

    def resolve_string(s: str, container: Container, key: str | int) -> str:
        prev = None
        count = 0
        while s != prev and count < max_recursion_depth:
            prev = s
            s = PLACEHOLDER_PATTERN.sub(lambda m: replacement(m, container, key), s)
            count += 1
        if count == max_recursion_depth:
            raise ValueError(f"Too many nested placeholder expansions in key '{key}'.")
        # Finally, replace escaped braces with literal ones
        return s.replace("{{", "{").replace("}}", "}")

    stack: list[StackItem] = [(config, key, config) for key in config]

    while stack:
        container, key, context = stack.pop()
        value = container[key]  # type: ignore[assignment]

        if isinstance(value, str):
            new_value = resolve_string(value, container, key)
            container[key] = new_value

        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, (dict, list, str)):
                    stack.append((value, i, context))

        elif isinstance(value, dict):
            for subkey in value:
                stack.append((value, subkey, value))

    return config
