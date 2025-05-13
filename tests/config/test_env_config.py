from pathlib import Path

import pytest

from docbuild.config.env import load_env_config
from docbuild.constants import ENV_CONFIG_FILENAME


def repr_toml_value(value):
    """Render a Python value as a TOML-compatible string."""
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        raise TypeError(
            f"Unsupported type for TOML serialization: {type(value).__name__}"
        )


def write_toml_config(directory: Path, role: str, content: dict):
    filename = ENV_CONFIG_FILENAME.format(role=role)
    path = directory / filename
    lines = []

    for key, value in content.items():
        if isinstance(value, dict):
            # Section header
            lines.append(f"\n[{key}]")
            for subkey, subvalue in value.items():
                lines.append(f"{subkey} = {repr_toml_value(subvalue)}")
        else:
            lines.append(f"{key} = {repr_toml_value(value)}")

    toml_text = "\n".join(lines)
    path.write_text(toml_text)
    return path


## ---
def test_load_valid_prod_config(tmp_path: Path):
    config_data = {"env": "production"}
    write_toml_config(tmp_path, "production", config_data)

    result = load_env_config(tmp_path, role="prod")
    assert result["env"] == "production"


def test_load_first_matching_variant_priority(tmp_path: Path):
    # Lower-priority file
    write_toml_config(tmp_path, "p", {"env": "SHOULD NOT LOAD"})
    # Higher-priority file
    write_toml_config(tmp_path, "prod", {"env": "higher"})
    # Highest-priority file
    write_toml_config(tmp_path, "production", {"env": "correct"})

    result = load_env_config(tmp_path, role="prod")
    assert result["env"] == "correct"


def test_load_from_multiple_paths(tmp_path: Path):
    dir1 = tmp_path / "empty"
    dir2 = tmp_path / "configs"
    dir1.mkdir()
    dir2.mkdir()

    write_toml_config(dir2, "staging", {"env": "staging"})

    result = load_env_config(dir1, dir2, role="stage")
    assert result["env"] == "staging"


def test_invalid_role_raises_value_error(tmp_path: Path):
    with pytest.raises(ValueError, match="Unknown role"):
        load_env_config(tmp_path, role="dev")


def test_missing_config_raises_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="No config file found"):
        load_env_config(tmp_path, role="test")
