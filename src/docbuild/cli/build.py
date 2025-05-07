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
import click
from pydantic import ValidationError

from .context import DocBuildContext
from ..models.doctype import Doctype


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

    # click.echo(f"Our doctypes: {doctypes=}")
    for doctype_str in doctypes:

        try:
            doctype = Doctype.from_str(doctype_str)
            click.echo(f"Got {doctype}")
            processed_data.append(doctype)

        except ValidationError as e:
            click.secho(
                f"ERROR: Invalid input for {doctype_str!r}:", fg="red", err=True
            )
            for idx, err in enumerate(e.errors(), 1):
                loc = " → ".join(str(p) for p in err["loc"])
                msg = err["msg"]
                click.echo(f"  [{idx}] {loc}: {msg}", err=True)
            raise click.Abort()

        except ValueError as e:
            click.secho(
                f"ERROR: Invalid input for {doctype_str!r}:", fg="red", err=True
            )
            click.echo(e, err=True)
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
