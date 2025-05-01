import re

import click

from .__about__ import __version__


def parse_set(ctx, param, value):
    if not value:
        return None
    # Join all values and split by spaces, commas or semicolons
    items_str = " ".join(value)
    # Use regex to split by space, comma or semicolon
    parts = re.split(r"[ ,;]+", items_str.strip())
    return parts


def validate_set(ctx, param, value):
    if not value:
        return None
    # Accept one string containing product, docset, lang separated by space, comma or semicolon
    parts = re.split(r"[ ,;]+", value.strip())
    if len(parts) != 3:
        raise click.BadParameter(
            "The --set option must contain exactly three parts: PRODUCT, DOCSET, LANG separated by space, comma, or semicolon."
        )
    product, docset, lang = parts

    # Validate PRODUCT and DOCSET: letters, digits, dash or '*'
    name_pattern = re.compile(r"^[a-zA-Z0-9-]+$")
    if product != "*" and not name_pattern.match(product):
        raise click.BadParameter(
            "PRODUCT must contain only letters, digits, dashes, or be '*'."
        )
    if docset != "*" and not name_pattern.match(docset):
        raise click.BadParameter(
            "DOCSET must contain only letters, digits, dashes, or be '*'."
        )

    # Validate LANG: format like en-us, de-de (two lowercase letters - two lowercase letters)
    lang_pattern = re.compile(r"^[a-z]{2}-[a-z]{2}$")
    if not lang_pattern.match(lang):
        raise click.BadParameter("LANG must be a language code like 'en-us', 'de-de'.")

    return (product, docset, lang)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-v", count=True, help="Increase verbosity level. Can be used multiple times."
)
@click.option(
    "-r",
    "--role",
    type=click.Choice(
        ["production", "prod", "testing", "test", "staging", "stage"],
        case_sensitive=False,
    ),
    # required=True,
    default="production",
    help="Set the role to one of: production, testing, staging.",
)
@click.option(
    "--version", is_flag=True, help="Show the version of the script and exit."
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the config file.",
)
@click.option(
    "--set",
    "set_values",
    multiple=True,
    callback=validate_set,
    help="One or more of PRODUCT/DOCSET/LANG separated by space, comma or semicolon. "
    "PRODUCT and DOCSET can be '*' meaning 'all'.",
)
def cli(v, role, version, config, set_values):
    """Example CLI with multiple options using Click."""
    if version:
        click.echo(f"Version: {__version__}")
        ctx = click.get_current_context()
        ctx.exit()

    click.echo(f"Verbosity level: {v}")
    click.echo(f"Role: {role}")
    if config:
        click.echo(f"Config file: {config}")
    if set_values:
        click.echo(f"Set values: {set_values}")


if __name__ == "__main__":
    cli()
