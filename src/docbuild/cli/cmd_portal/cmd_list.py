"""Portal management commands for the docbuild CLI."""

import asyncio
from collections import defaultdict

import click
from lxml import etree  # type: ignore
from rich.console import Console
from rich.tree import Tree

from docbuild.cli.context import DocBuildContext
from docbuild.config.xml.list import list_all_deliverables
from docbuild.models.deliverable import Deliverable
from docbuild.models.doctype import Doctype


def build_hierarchy(
    deliverables: list[Deliverable],
) -> dict[str, dict[str, dict[str, list[str]]]]:
    """Group a list of Deliverable domain objects into a nested dictionary structure.

    :param deliverables: A list of Deliverable models to organize.
    :return: A nested dictionary structured as {lang: {product: {docset: [deliverable titles]}}}.
    """
    hierarchy: dict[str, dict[str, dict[str, list[str]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    for deliverable in deliverables:
        # Pull facts via the clean Deliverable XML view facade
        lang = str(deliverable.xml.lang)
        product = deliverable.xml.productid or "unknown-product"
        docset = deliverable.xml.docsetid or "unknown-docset"

        # Determine a compact leaf string using ID and DC file metadata
        d_id = deliverable.xml.node.get("id", "unnamed-deliverable")
        dc_file = deliverable.xml.dcfile
        display_name = f"{d_id} ({dc_file})" if dc_file else d_id

        hierarchy[lang][product][docset].append(display_name)

    return hierarchy


async def async_list_cmd(ctx: DocBuildContext, doctypes: tuple[str, ...], console: Console) -> None:
    """Async worker to fetch the XML, parse Doctypes, and build the tree.

    :param ctx: The DocBuildContext containing CLI options and config.
    :param doctypes: A tuple of doctype strings passed as arguments to the command.
    :param console: The Rich Console object for outputting the tree.
    """
    # 1. Parse Doctypes
    parsed_doctypes = None
    if doctypes:
        try:
            parsed_doctypes = [Doctype.from_str(dt) for dt in doctypes]
        except ValueError as e:
            console.print(f"[red]Error parsing doctype:[/red] {e}")
            raise click.Abort() from e

    # 2. Get XML Tree
    config_dir = ctx.envconfig.paths.config_dir.expanduser()  # type: ignore
    portal_xml_path = config_dir / "portal.xml"

    if not portal_xml_path.exists():
        console.print(f"[red]Error: Main portal config not found at {portal_xml_path}[/red]")
        raise click.Abort()

    try:
        tree = etree.parse(portal_xml_path)
        tree.xinclude()
    except Exception as e:
        console.print(f"[red]Error loading XML schema:[/red] {e}")
        raise click.Abort() from e

    # 3. Fetch and wrap Deliverables into Domain Objects
    raw_nodes = list(list_all_deliverables(tree, parsed_doctypes))
    deliverables = [Deliverable(_node=node) for node in raw_nodes]

    if not deliverables:
        console.print("[yellow]No deliverables found matching the criteria.[/yellow]")
        return

    # 4. Group data for Rich Tree
    hierarchy = build_hierarchy(deliverables)

    # 5. Build and print the Rich Tree
    for lang, products in sorted(hierarchy.items()):
        root_tree = Tree(f"[bold blue]{lang}/[/bold blue]")

        for product, docsets in sorted(products.items()):
            prod_branch = root_tree.add(f"[bold]{product}[/bold]")

            for docset, delivs in sorted(docsets.items()):
                docset_branch = prod_branch.add(f"[cyan]{docset}[/cyan]")

                for display_name in sorted(delivs):
                    docset_branch.add(display_name)

        console.print(root_tree)
        console.print()


@click.command(name="list")
@click.argument("doctypes", nargs=-1)
@click.pass_obj
def list_cmd(ctx: DocBuildContext, doctypes: tuple[str, ...]) -> None:
    """List products, docsets, and deliverables from the portal config.

    Accepts optional DOCTYPE arguments to filter the output.
    Format: [PRODUCT]/[DOCSETS]@[LIFECYCLES]/[LANGS]

    Example:
        docbuild portal list sles/15-SP6

    :param ctx: The DocBuildContext passed from the CLI, containing config and options.
    :param doctypes: A tuple of doctype strings passed as arguments to the command.
    """
    console = Console()
    asyncio.run(async_list_cmd(ctx, doctypes, console))
