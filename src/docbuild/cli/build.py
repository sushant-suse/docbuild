"""Build a document

A document (or "doctype") consists of "[PRODUCT]/[DOCSET][@LIFECYCLES]/LANGS"
with the following properties:

\b
  * (Optional) PRODUCT is the product. To mark "ALL" products, omit the product
    or use "*"
  * (Optional) DOCSET is the docset, usually the version or release of a product.
    To mark "ALL" docsets, omit the docset or use "*".
  * (Optional) LIFECYCLES marks a list of lifecycles separated by comma or pipe symbol.
    A lifecycle can be one of the values 'supported', 'unsupported', 'beta',
    or 'hidden'.
  * LANGS marks a list of languages separated by comma. Every single language
    contains a LANGUAGE-COUNTRY syntax, for example 'en-us', 'de-de' etc.

Examples of the doctypes syntax:

\b
  * "//en-us"
    Builds all supported deliverables for English
  * "sles/*/en-us"
    Builds only SLES deliverables which are supported and in English
  * "sles/*@unsupported/en-us,de-de"
    Builds all English and German SLES releases which are unsupported
  * "sles/@beta|supported/de-de"
    Build all docsets that are supported and beta for German SLES.
  * "sles/@beta,supported/de-de"
    Same as the previous one, but with comma as the separator between
    the lifecycle states.
"""
import click
from pydantic import ValidationError

from .context import DocBuildContext
from ..models.doctype import Doctype


def is_subsumed_by(specific: Doctype, general: Doctype) -> bool:
    """Compares two Doctype arguments if specific is contained in general

    If specific is "sles/15-SP6/en-us" and general is "sles/*/en-us",
    then the first would be included in the latter.

    :param specific: the specific Doctype
    :param general: the general Doctype
    :return: True, if specific is included in general, otherwise False
    """
    return all(
        g == "*" or s == g
        for s, g in zip(
            [specific.product, specific.docset, specific.lifecycle, specific.langs],
            [general.product, general.docset, general.lifecycle, general.langs],
        )
    )


def filter_redundant_doctypes(doctypes: list[Doctype]) -> list[Doctype]:
    """Filter redundant Doctype entries

    For example, if you have sles/15-SP6/en-us and sles/*/en-us, then
    the first would be redundant as it is already included in the second.
    """
    result = []

    for dt in doctypes:
        if any(other != dt and is_subsumed_by(dt, other) for other in doctypes):
            # dt is subsumed by another doctype -> skip
            continue
        result.append(dt)

    return result


# --- Callback Function ---
def validate_set(ctx: click.Context,
    param: click.Parameter,
    doctypes: tuple[str, ...]
) -> list[Doctype]:
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

        except ValidationError as err:
            for error in err.errors():
                field = error["loc"][0]
                msg = error["msg"]
                hint = Doctype.model_fields[field].description
                example = Doctype.model_fields[field].examples
                click.secho(
                    f"ERROR in '{field}': {msg}",
                    fg="red",
                    err=True,
                )
                if hint:
                    click.echo(f"  → Hint: {hint}")
                if example:
                    click.echo(f"  → Examples: {', '.join(example)}")
                click.echo()

            #for idx, err in enumerate(e.errors(), 1):
            #    loc = " → ".join(str(p) for p in err["loc"])
            #    msg = err["msg"]
            #    click.echo(f"  [{idx}] {loc}: {msg}", err=True)
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

    processed_data = filter_redundant_doctypes(processed_data)
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
    click.echo(f"{context.configfile=}")
