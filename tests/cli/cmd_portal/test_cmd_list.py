"""Tests for the portal list command."""

from unittest.mock import MagicMock

from click.testing import CliRunner

from docbuild.cli.cmd_portal.cmd_list import list_cmd
from docbuild.cli.context import DocBuildContext


def test_portal_list_help() -> None:
    """Test that the help menu renders correctly for 'portal list'."""
    runner = CliRunner()
    result = runner.invoke(list_cmd, ["--help"])

    assert result.exit_code == 0
    assert "List products, docsets, and deliverables from the portal config." in result.output
    assert "Format:" in result.output
    assert "[PRODUCT]" in result.output


def test_portal_list_no_main_config(tmp_path) -> None:
    """Test that the command gracefully aborts if portal.xml is not found."""
    runner = CliRunner()

    mock_ctx = DocBuildContext()
    mock_ctx.envconfig = MagicMock()
    mock_ctx.envconfig.paths.config_dir.expanduser.return_value = tmp_path

    result = runner.invoke(list_cmd, obj=mock_ctx)

    assert result.exit_code != 0
    assert "Error: Main portal config not found at" in result.output


def test_portal_list_invalid_doctype() -> None:
    """Test that the command gracefully aborts if an invalid doctype is passed."""
    runner = CliRunner()
    mock_ctx = DocBuildContext()

    result = runner.invoke(list_cmd, ["invalid_doctype_format!"], obj=mock_ctx)

    assert result.exit_code != 0
    assert "Error parsing doctype:" in result.output


def test_portal_list_malformed_xml(tmp_path) -> None:
    """Test that the command gracefully aborts if the portal.xml contains unparseable syntax."""
    runner = CliRunner()

    portal_file = tmp_path / "portal.xml"
    portal_file.write_text("<portal><broken-tag>unclosed", encoding="utf-8")

    mock_ctx = DocBuildContext()
    mock_ctx.envconfig = MagicMock()
    mock_ctx.envconfig.paths.config_dir.expanduser.return_value = tmp_path

    result = runner.invoke(list_cmd, obj=mock_ctx)

    assert result.exit_code != 0
    assert "Error loading XML schema:" in result.output


def test_portal_list_success(tmp_path) -> None:
    """Test that 'portal list' parses a valid configuration and displays the tree structure."""
    runner = CliRunner()

    # Minimal valid structure with an active deliverable tag
    portal_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<portal schemaversion="7.0">\n'
        '    <categories>\n'
        '        <category lang="en-us">\n'
        '            <language id="base" title="General Documentation"/>\n'
        '        </category>\n'
        '    </categories>\n'
        '    <productfamilies>\n'
        '        <item id="os">Operating Systems</item>\n'
        '    </productfamilies>\n'
        '    <series>\n'
        '        <item id="products">Main Products</item>\n'
        '    </series>\n'
        '    <product id="sles" series="products" family="os">\n'
        '        <name>SUSE Linux Enterprise Server</name>\n'
        '        <maintainers>\n'
        '            <contact>doc-team@example.com</contact>\n'
        '        </maintainers>\n'
        '        <docset id="15-SP6" path="15-SP6" lifecycle="supported">\n'
        '            <version>15 SP6</version>\n'
        '            <external/>\n'
        '            <builddocs>\n'
        '                <language lang="en-us">\n'
        '                    <branch>main</branch>\n'
        '                    <deliverable id="admin_guide">\n'
        '                        <dc file="DC-admin-guide"/>\n'
        '                    </deliverable>\n'
        '                </language>\n'
        '            </builddocs>\n'
        '        </docset>\n'
        '    </product>\n'
        '</portal>\n'
    )
    
    portal_file = tmp_path / "portal.xml"
    portal_file.write_text(portal_content, encoding="utf-8")

    mock_ctx = DocBuildContext()
    mock_ctx.envconfig = MagicMock()
    mock_ctx.envconfig.paths.config_dir.expanduser.return_value = tmp_path

    result = runner.invoke(list_cmd, obj=mock_ctx)

    assert result.exit_code == 0
    assert "en-us" in result.output
    assert "sles" in result.output
    assert "15-SP6" in result.output
    assert "admin_guide (DC-admin-guide)" in result.output


def test_portal_list_no_matching_deliverables(tmp_path) -> None:
    """Test that the command displays a yellow notice if filters yield zero results."""
    runner = CliRunner()

    # Valid structure but completely missing <deliverable> to force an empty return payload safely
    portal_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<portal schemaversion="7.0">\n'
        '    <categories><category lang="en-us"><language id="base" title="Gen"/></category></categories>\n'
        '    <productfamilies><item id="os">OS</item></productfamilies>\n'
        '    <series><item id="products">Main</item></series>\n'
        '    <product id="sles" series="products" family="os">\n'
        '        <name>SUSE</name><maintainers><contact>a@b.com</contact></maintainers>\n'
        '        <docset id="15-SP6" path="15-SP6" lifecycle="supported">\n'
        '            <version>15</version><external/>\n'
        '            <builddocs>\n'
        '                <language lang="en-us">\n'
        '                    <branch>main</branch>\n'
        '                </language>\n'
        '            </builddocs>\n'
        '        </docset>\n'
        '    </product>\n'
        '</portal>\n'
    )
    portal_file = tmp_path / "portal.xml"
    portal_file.write_text(portal_content, encoding="utf-8")

    mock_ctx = DocBuildContext()
    mock_ctx.envconfig = MagicMock()
    mock_ctx.envconfig.paths.config_dir.expanduser.return_value = tmp_path

    result = runner.invoke(list_cmd, obj=mock_ctx)

    assert result.exit_code == 0
    assert "No deliverables found matching the criteria." in result.output