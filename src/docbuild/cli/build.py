"""Build a document

\b
A document (or "doctype") consists of PRODUCT/DOCSET@LIFECYCLE/LANGS
with the following properties:

\b
  * PRODUCT is the product. It can be omitted. Either use '*' or just use '/'
  * DOCSET is the docset, usually the version or release of a product. It
    can be omitted. Either use '*' or just use '/'
  * LIFECYCLE marks the lifecycle of the product. It can be one of the
    values 'supported', 'unsupported', 'beta', or 'hidden'
  * LANGS marks a list of languages separated by comma. Every single language
    contains a LANGUAGE-COUNTRY syntax, for example 'en-us', 'de-de' etc.

Examples of the doctypes syntax:

\b
  * "//en-us"
    Builds all supported deliverables for English
  * "sles/*/en-us"
    Builds only SLES deliverables which are supported and in English
  * "sles/*@unsupported/en-us"

"""
import re

import click
from pydantic import ValidationError

from .context import DocBuildContext
from ..constants import (
    DEFAULT_LIFECYCLE,
)

from ..models.doctype import Doctype

# Pre-compile regex for efficiency
DOCTYPE_REGEX = re.compile(
    r"^([^/@]*|\*)?/([^/@]*|\*)?(?:@([a-z]+))?/(\*|[\w-]+(?:,[\w-]+)*)$"
)


# --- Callback Function ---
def validate_set(ctx: click.Context,
    param: click.Parameter,
    doctypes: tuple[str, ...]
) -> list[tuple[str, str, str, list[str]]]:
    """
    Click callback function to validate a list of doctype strings.

    Each string must conform to the format: PRODUCT/DOCSET@LIFECYCLE/LANGS
    LANGS can be a single language code, a comma-separated list (no spaces), or '*' for all.
    Defaults and wildcards (*) are handled.
    """
    processed_data = []  # Store successfully parsed/validated data

    click.echo("validate_set")

    if not doctypes:
        return []

    click.echo(f"Our doctypes: {doctypes=}")
    for doctype_str in doctypes:
        match = DOCTYPE_REGEX.match(doctype_str)

        if not match:
            raise click.BadParameter(
                f"Invalid format for '{doctype_str}'.\n"
                f"Expected format: 'PRODUCT/DOCSET@LIFECYCLE/LANGS'.\n"
                f"LANGS can be 'lang1', 'lang1,lang2,...', or '*'.\n"
                f"Examples: 'sles/docs@beta/en-us', '*/ug/de-de,fr-fr', '//en-us,ja-jp', '//de-de', '//*'.\n"
                f"Use '*' for all products or docsets. Lifecycle (@...) is optional (defaults to '@{DEFAULT_LIFECYCLE}').",
                ctx=ctx,
                param=param,
            )

        # Extract matched groups
        product_str, docset_str, lifecycle_str, langs_raw_str = match.groups()
        if product_str is None:
            product_str: str = "*"
        if lifecycle_str is None:
            lifecycle_str = "supported"
        if langs_raw_str is None:
            langs_raw_str = "en-us"

        click.echo(f"""Received these values:
    {product_str=}
    {docset_str=}
    {lifecycle_str=}
    {langs_raw_str=}""")

        try:
            doctype = Doctype(
                product=product_str,  # type: ignore
                docset=docset_str,
                lifecycle=lifecycle_str,  # type: ignore
                langs=langs_raw_str.split(","),  # type: ignore
            )
            processed_data.append(doctype)
        except ValidationError as e:
            click.secho(f"ERROR: Invalid input for {doctype_str!r}:", fg="red")
            for idx, err in enumerate(e.errors(), 1):
                loc = " → ".join(str(p) for p in err["loc"])
                msg = err["msg"]
                click.echo(f"  [{idx}] {loc}: {msg}")
            raise click.Abort()

    # --- Optional: Post-validation checks across all inputs ---
    # This part becomes more complex if you need to merge/check '*' against lists.
    # For now, we'll just validate each argument independently.
    # You might handle the combination logic in the main command.

    ctx.obj.doctypes = processed_data
    return processed_data


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
