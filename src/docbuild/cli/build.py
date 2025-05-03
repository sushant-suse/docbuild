import re

import click
from .context import DocBuildContext
from ..constants import DEFAULT_LANGS, RE_SEPARATORS, SINGLE_DOCTYPE_REGEX


def validate_set(ctx, param, value):
    if not value:
        return None
    # Accept one string containing product, docset, lang separated by space, comma or semicolon
    click.echo(f"validate_set: {param=} {value=}")
    doctypes = RE_SEPARATORS.split(value.strip())

    result = []
    click.echo(f"{doctypes=}")
    for dt in doctypes:
        match = SINGLE_DOCTYPE_REGEX.match(dt)
        if not match:
            click.echo(click.style("ERROR:", fg="red"), nl=False)
            click.echo(f"The string {dt!r} contains a syntax error")
            raise click.BadParameter(f"The string {dt!r} is invalid.")
        product, docset, lifecycle, langs = match.groups()
        # Use defaults
        if product is None:
            product = "*"
        if docset is None:
            docset = "*"
        if lifecycle is None:
            lifecycle = "supported"
        if langs is None:
            langs = DEFAULT_LANGS[0]
        langs = langs.split(",")
        result.append((product, docset, lifecycle, langs))

    click.echo(f"{result=}")
    ctx.params["doctypes"] = result

    return result


@click.command()
@click.option(
    "--doctypes",
    "doctypes",
    callback=validate_set,
    help=(
        "One or more of PRODUCT/DOCSET@LIFECYCLE/LANG triplets, separated by space, "
        "comma or semicolon. PRODUCT and DOCSET can be '*' meaning 'all'."
    ),
)
@click.pass_context
def build(ctx, doctypes):
    context: DocBuildContext = ctx.obj
    click.echo(f"[BUILD] Verbosity: {context.verbosity}")
    click.echo(f"{doctypes=}")
