import ast

from docbuild.cli.config.app import app


def test_config_app(context, runner):
    context.appconfigfiles = ['/tmp/app1.toml', '/tmp/app2.toml']
    context.appconfig = {'foo': 'bar', 'baz': [1, 2, 3]}

    # Run the command with the fake context
    result = runner.invoke(app, obj=context)

    assert result.exit_code == 0
    assert (
        "# Application config files '/tmp/app1.toml, /tmp/app2.toml'" in result.output
    )

    lines = result.output.splitlines()
    pretty_dict_str = '\n'.join(lines[1:]).strip()
    # Convert to dict
    output_dict = ast.literal_eval(pretty_dict_str)
    assert output_dict == {'foo': 'bar', 'baz': [1, 2, 3]}

