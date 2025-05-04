"""Build a document

\b
A document (or "doctype") consists of PRODUCT/DOCSET@LIFECYCLE/LANG
with the following properties:

\b
  * PRODUCT is the product. It can be omitted. Either use '*' or just use '/'
  * DOCSET is the docset, usually the version or release of a product. It
    can be omitted. Either use '*' or just use '/'
  * LIFECYCLE marks the lifecycle of the product. It can be one of the
    values 'supported', 'unsupported', 'beta', or 'hidden'
  * LANG marks the language. To use more than one language, separate each
    language with a comma. Every LANG contains a LANGUAGE-COUNTRY syntax,
    for example 'en-us', 'de-de' etc.

Examples of the doctypes syntax:

\b
  * "//en-us"
    Builds all supported deliverables for English
  * "sles/*/en-us"
    Builds only SLES deliverables which are supported and in English
  * "sles/*@unsupported/en-us"

"""

import click
from .context import DocBuildContext
from ..constants import (
    DEFAULT_LANGS,
    SINGLE_DOCTYPE_REGEX,
)


def validate_set(ctx : click.Context, param: click.Argument, values: tuple[str]):
    if not values:
        return None
    # Accept one string containing product, docset, lang separated by space, comma or semicolon
    if ctx.obj.debug:
        click.echo(f"validate_set: {param=} {values=}")
        click.echo(f"Context: {ctx.obj}")
        click.echo(f"{param.default=} {param.envvar=}")
        click.echo(f"{SINGLE_DOCTYPE_REGEX.pattern=}")

    result = []
    for doctype in values:
        match = SINGLE_DOCTYPE_REGEX.match(doctype)
        if not match:
            #click.echo(click.style("ERROR:", fg="red"), nl=False, err=True)
            # click.echo(click.style("ERROR:", fg="red"), nl=False)
            #click.echo(f"The string {doctype!r} contains a syntax error", err=True)
            # ctx.exit(10)
            raise click.ClickException(
                f"The doctype {doctype!r} contains a syntax error"
            )

        product, docset, lifecycle, langs = match.groups()
        click.echo(f"Found {product=}, {docset=}, {lifecycle=}, {langs=}")
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
    ctx.obj.doctypes = result

    return result


@click.command(
    help=__doc__
)
@click.argument(
    "doctypes",
    nargs=-1,
    callback=validate_set,
    #help=(
    #    "One or more of PRODUCT/DOCSET@LIFECYCLE/LANG triplets, separated by space, "
    #    "comma or semicolon. PRODUCT and DOCSET can be '*' meaning 'all'."
    #),
)
@click.pass_context
def build(ctx, doctypes):
    context: DocBuildContext = ctx.obj

    click.echo(f"[BUILD] Verbosity: {context.verbosity}")
    click.echo(f"{context=}")
