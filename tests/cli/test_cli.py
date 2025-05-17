from pathlib import Path

import pytest

from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from docbuild.cli.cli import cli


@pytest.mark.skip("Need to be adjust when env is refactored")
def test_cli_load_app_config_called(tmp_path):
    runner = CliRunner()

    config_toml = tmp_path / "config.toml"
    config_toml.write_text('test = "found"')

    def fake_loader(*paths, default=None):
        print("Called with:", paths)
        return {"mocked": True, "config_paths": paths, "used_default": default}

    mock_loader = MagicMock(side_effect=fake_loader)

    # Patch where the function is *used*, not where it's defined
    with patch("docbuild.cli.cli.load_app_config",
                new=mock_loader,
               ) as mock_load:
        mock_cfg = MagicMock()
        mock_load.return_value = mock_cfg

        result = runner.invoke(cli, ["--config", "config.toml", "test"])

        assert result.exit_code == 0
        mock_loader.assert_called_once()
        assert str(mock_loader.call_args[0][0]) == "config.toml"
        assert "mocked" in result.output


def test_main_entry_point(tmp_path):
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "docbuild.cli.cli", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
    assert "Main CLI tool" in result.stdout