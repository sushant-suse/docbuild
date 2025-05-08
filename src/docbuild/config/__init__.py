from pathlib import Path

# import tomlkit as toml
import tomllib as toml

from ..constants import APP_CONFIG_PATHS, APP_CONFIG_FILENAME
from .merge import deep_merge


def load_app_config(paths: tuple[str|Path, ...]=APP_CONFIG_PATHS) -> dict:
    """Load the app's config files and merge all content regardless
       of the nesting level

       :param paths: the paths to look for config files
       :return: the merged dictionary
    """
    configs = []
    for path in paths:
        path = Path(path).expanduser() / APP_CONFIG_FILENAME
        if path.exists():
            with path.open("rb") as f:
                configs.append(toml.load(f))
        else:
            configs.append({})  # fallback empty

    return deep_merge(*configs)