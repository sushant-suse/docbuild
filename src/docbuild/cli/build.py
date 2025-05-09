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
from collections import defaultdict
from itertools import chain

import click
from pydantic import ValidationError

from .context import DocBuildContext
from ..models.doctype import Doctype
from ..models.language import LanguageCode


def is_subsumed_by(existing: Doctype, candidate: Doctype) -> bool:
    """
    Checks if the candidate Doctype can be considered a more general version
    of the existing Doctype.
    """
    # Implement logic to check subsumption between two doctypes
    # This could compare `product`, `docset`, `langs`, etc.
    return (
        (candidate.product == "*" or existing.product == candidate.product)
        and "*" in candidate.docset
        or set(candidate.docset).issubset(existing.docset)
        and "*" in candidate.langs
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


def merge_doctypes(*doctypes: Doctype) -> list[Doctype]:
    """Merge and deduplicate Doctypes intelligently."""

    # Group by (product, lifecycle)
    grouped: dict[tuple, list[Doctype]] = defaultdict(list)

    for dt in doctypes:
        key = (dt.product, tuple(sorted(dt.docset)), dt.lifecycle)
        grouped[key].append(dt)

    merged: list[Doctype] = []

    for (product, docset, lifecycle), group in grouped.items():
        # Union all langs
        all_langs = set(chain.from_iterable(dt.langs for dt in group))
        merged.append(
            Doctype(
                product=product,
                docset=list(docset),
                lifecycle=lifecycle.name,
                langs=all_langs,
            )
        )

    return merged

    for (product, lifecycle), group in grouped.items():
        merged_docsets = set()
        merged_langs = set()

        for dt in group:
            merged_docsets.update(dt.docset)
            merged_langs.update(dt.langs)

        # If "*" is present, collapse to wildcard
        docset = sorted(["*"] if "*" in merged_docsets else sorted(merged_docsets))
        langs = (
            ["*"]
            if LanguageCode("*") in merged_langs
            else sorted(merged_langs, key=str)
        )

        result.append(
            Doctype(
                product=product,
                docset=docset,
                lifecycle=lifecycle.name,
                langs=langs,
            )
        )

    return result


    """
    Merge the provided doctypes while ensuring that we keep distinct entries
    """
    result = []
    )


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

    # processed_data = filter_redundant_doctypes(processed_data)
    processed_data = merge_doctypes(*processed_data)
    ctx.obj.doctypes = processed_data
    return processed_data


@click.command(
    help=__doc__
)
@click.argument(
    "doctypes",
    nargs=-1,
    callback=validate_set,
)
@click.pass_context
def build(ctx, doctypes):
    """Subcommand build"""
    context: DocBuildContext = ctx.obj

    click.echo(f"[BUILD] Verbosity: {context.verbosity}")
    click.echo(f"{context=}")
    click.echo(f"{context.configfile=}")
