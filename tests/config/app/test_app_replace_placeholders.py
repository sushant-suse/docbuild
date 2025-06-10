import re

import pytest

from docbuild.config.app import replace_placeholders


def test_replace_placeholders():
    config = {
        'server': {'name': 'example.com', 'url': 'https://{server.name}'},
        'paths': {
            'config_dir': '/etc/myapp',
            'tmp': {'tmp_base_path': '/tmp/myapp'},
            'full_tmp_path': '{paths.tmp.tmp_base_path}/session',
        },
        'logging': {
            'log_dir': '{paths.config_dir}/logs',
            'tmp_base_path': '/var/tmp',
            # Should resolve within this section if key exists:
            'temp_dir': '{tmp_base_path}',
        },
    }

    expected = {
        "server": {"name": "example.com", "url": "https://example.com"},
        "paths": {
            "config_dir": "/etc/myapp",
            "tmp": {"tmp_base_path": "/tmp/myapp"},
            "full_tmp_path": "/tmp/myapp/session",
        },
        "logging": {
            "log_dir": "/etc/myapp/logs",
            "tmp_base_path": "/var/tmp",
            "temp_dir": "/var/tmp",
        },
    }

    result = replace_placeholders(config)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_missing_key_in_current_section():
    config = {
        "database": {
            "host": "localhost",
            # 'user' is missing in this section
            "url": "postgres://{user}@{host}/mydb",
        },
        "user": "admin",
    }

    with pytest.raises(
        KeyError,
        match=re.escape(
            "While resolving '{user}' in 'url': key 'user' "
            "not found in current section.",
        ),
    ):
        replace_placeholders(config)


def test_unresolved_key_in_config():
    config = {
        "server": {"name": "example.com", "url": "https://{server.name}"},
        "paths": {
            "config_dir": "/etc/myapp",
            "tmp": {"tmp_base_path": "/tmp/myapp"},
            # 'session' is missing in this section
            "full_tmp_path": "{paths.tmp.session}/session",
        },
    }

    with pytest.raises(
        KeyError,
        match=re.escape(
            "While resolving '{paths.tmp.session}' in 'full_tmp_path': missing key "
            "'session' in path 'paths.tmp.session'.",
        ),
    ):
        replace_placeholders(config)


def test_placeholders_in_list():
    config = {
        "paths": {
            "config_dir": "/etc/myapp",
        },
        "resources": {
            "files": [
                "{paths.config_dir}/app.yaml",
                "{paths.config_dir}/db.yaml",
                "static/style.css",
            ],
        },
    }

    expected = {
        "paths": {
            "config_dir": "/etc/myapp",
        },
        "resources": {
            "files": ["/etc/myapp/app.yaml", "/etc/myapp/db.yaml", "static/style.css"],
        },
    }

    result = replace_placeholders(config)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_literal_values_are_untouched():
    config = {
        "defaults": {"enabled": True, "retries": 3, "timeout": 5.5, "optional": None},
    }

    expected = {
        "defaults": {"enabled": True, "retries": 3, "timeout": 5.5, "optional": None},
    }

    result = replace_placeholders(config)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_placeholder_path_is_not_dict():
    config = {
        "server": {"name": "myserver", "ip": "127.0.0.1"},
        "paths": {
            "tmp": "not_a_dict",
            "path": "{paths.tmp.value}",  # .value should fail
        },
    }

    with pytest.raises(
        KeyError,
        match=re.escape(
            "While resolving '{paths.tmp.value}' in 'path': 'paths.tmp.value' is not "
            "a dictionary (got type str).",
        ),
    ):
        replace_placeholders(config)


def test_chained_placeholder_resolution():
    data = {
        "paths": {
            "tmp": {
                "tmp_base_path": "/tmp/docbuild",
                "tmp_path": "{tmp_base_path}/doc-example-com",
                "tmp_deliverable_path": "{tmp_path}/deliverable/",
            },
        },
    }

    result = replace_placeholders(data)
    tmp = result["paths"]["tmp"]
    assert tmp["tmp_base_path"] == "/tmp/docbuild"
    assert tmp["tmp_path"] == "/tmp/docbuild/doc-example-com"
    assert tmp["tmp_deliverable_path"] == "/tmp/docbuild/doc-example-com/deliverable/"


def test_too_many_nested_placeholder_expansions():
    data = {
        "section": {
            "a": "{b}",
            "b": "{a}",
        },
    }
    with pytest.raises(ValueError, match="Too many nested placeholder expansions"):
        replace_placeholders(data)


def test_chained_cross_section_placeholders():
    config = {
        "build": {
            "output": "{paths.tmp_deliverable_path}",
        },
        "paths": {
            "tmp_base_path": "/tmp/docbuild",
            "tmp_path": "{tmp_base_path}/doc-example-com",
            "tmp_deliverable_path": "{paths.tmp_path}/deliverable/",
        },
    }

    result = replace_placeholders(config)
    assert result["build"]["output"] == "/tmp/docbuild/doc-example-com/deliverable/"


def test_escaped_braces():
    config = {"section": {"key": "This is a literal brace: {{not_a_placeholder}}"}}
    result = replace_placeholders(config)
    assert result["section"]["key"] == "This is a literal brace: {not_a_placeholder}"
