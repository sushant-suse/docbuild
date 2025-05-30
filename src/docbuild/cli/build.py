"""Build a document.

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

from ..models.doctype import Doctype
from .context import DocBuildContext


def is_subsumed_by(existing: Doctype, candidate: Doctype) -> bool:
    """Check if candidate is more general than existing doctype."""
    return (
        (candidate.product in ["*", existing.product] and "*" in candidate.docset) or
        (set(candidate.docset).issubset(existing.docset) and "*" in candidate.langs)
    )
    # This could compare `product`, `docset`, `langs`, etc.
    return (
        ((candidate.product == "*" or existing.product == candidate.product)
        and "*" in candidate.docset)
        or (set(candidate.docset).issubset(existing.docset)
        and "*" in candidate.langs)
    )


def filter_redundant_doctypes(doctypes: list[Doctype]) -> list[Doctype]:
    """Filter redundant Doctype entries.

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
    """Merge a list of Doctype instances into a minimal set of non-redundant entries.

    Strategy:
    - For each incoming Doctype `dt`, compare it to the existing `result` list.
    - If any existing Doctype can absorb `dt`, extend its docset/langs as needed.
    - If `dt` can absorb an existing one, replace it.
    - Otherwise, keep both.
    - Wildcards ("*") are treated as "contains all" and will cause merging
      if overlap exists.
    - `docset` and `langs` are always sorted lists.

    Examples:
        'foo/1,2/en-us' + 'foo/*/en-us' => 'foo/*/en-us'
        'foo/1,2/*' + 'foo/1/en-us' => 'foo/1,2/*'

    """
    result: list[Doctype] = []
    # merged: bool = False

    for dt in doctypes:
        # merged = False
        new_result = []

        for existing in result:
            if dt.product != existing.product:
                new_result.append(existing)
                continue

            # Check for docset/langs intersection (wildcards count as overlap)
            docset_overlap = (
                "*" in dt.docset
                or "*" in existing.docset
                or bool(set(dt.docset) & set(existing.docset))
            )
            langs_overlap = (
                "*" in dt.langs
                or "*" in existing.langs
                or bool(set(dt.langs) & set(existing.langs))
            )

            if docset_overlap and langs_overlap:
                # Merge the entries
                docset = (
                    ["*"]
                    if "*" in dt.docset or "*" in existing.docset
                    else sorted(set(dt.docset + existing.docset))
                )
                langs = (
                    ["*"]
                    if "*" in dt.langs or "*" in existing.langs
                    else sorted(set(dt.langs + existing.langs))
                )
                dt = Doctype(
                    product=dt.product,
                    docset=docset,
                    langs=langs,
                    lifecycle=dt.lifecycle,  # assuming same lifecycle
                )
                # merged = True
            else:
                new_result.append(existing)

        new_result.append(dt)
        result = new_result

    return result


def merge_two_doctypes(dt1: Doctype, dt2: Doctype,
                       ) -> list[Doctype]:
    """Merge two Doctype instances into a minimal set of non-redundant entries."""
    if (dt1.product != dt2.product or
        dt1.lifecycle != dt2.lifecycle or
        dt1.langs != dt2.langs
        ):
        return [dt1, dt2]

    # The two doctypes distinguish solely on their docsets. Let's merge
    # them
    return [Doctype(
        product=dt1.product,
        docset=list(set(dt1.docset + dt2.docset)),
        lifecycle=dt1.lifecycle,
        langs=dt1.langs,
        ),
    ]


# --- Callback Function ---
def validate_doctypes(ctx: click.Context,
    param: click.Parameter|None,
    doctypes: tuple[str, ...],
) -> list[Doctype]:
    """Click callback function to validate a list of doctype strings.

    Each string must conform to the format: PRODUCT/DOCSET@LIFECYCLE/LANGS
    LANGS can be a single language code, a comma-separated list (no spaces),
    or '*' for all.
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
                # Convert to string to ensure it works as dictionary key
                field_name = str(field)
                msg = error["msg"]
                hint = Doctype.model_fields[field_name].description
                example = Doctype.model_fields[field_name].examples
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
            raise click.Abort(err) from err

        #except ValueError as e:
        #    click.secho(
        #        f"ERROR: Invalid input for {doctype_str!r}:", fg="red", err=True
        #    )
        #    click.echo(e, err=True)
        #    raise click.Abort()

    # --- Optional: Post-validation checks across all inputs ---
    # This part becomes more complex if you need to merge/check '*' against lists.
    # For now, we'll just validate each argument independently.
    # You might handle the combination logic in the main command.

    # processed_data = filter_redundant_doctypes(processed_data)
    processed_data = merge_doctypes(*processed_data)
    ctx.obj.doctypes = processed_data
    return processed_data


@click.command(
    help=__doc__,
)
@click.argument(
    "doctypes",
    nargs=-1,
    callback=validate_doctypes,
)
@click.pass_context
def build(ctx: click.Context, doctypes: tuple[str, ...]) -> None:
    """Subcommand build."""
    ctx.ensure_object(DocBuildContext)
    context: DocBuildContext = ctx.obj

    click.echo(f"[BUILD] Verbosity: {context.verbose}")
    click.echo(f"{context=}")
    click.echo(f"{context.appconfigfiles=}")
