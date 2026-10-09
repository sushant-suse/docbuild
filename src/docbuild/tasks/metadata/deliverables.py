"""Deliverable collection helpers for metadata processing."""

import logging

from lxml import etree

from docbuild.constants import XML_ID
from docbuild.models.deliverable import Deliverable
from docbuild.models.doctype import Doctype

log = logging.getLogger(__name__)


def get_deliverable_from_doctype(
    root: etree._ElementTree,
    doctype: Doctype,
) -> list[Deliverable]:
    """Get deliverable from doctype.

    :param root: The stitched XML node containing configuration.
    :param doctype: The Doctype object to process.
    :return: A list of deliverables for the given doctype.
    """
    languages = root.getroot().xpath(f"./{doctype.xpath()}")

    deliverables = []
    for language in languages:
        nodes = language.findall("deliverable")

        # 1. If a translation has any `<deliverable>`, it fully replaces the English list.
        if nodes:
            deliverables.extend(Deliverable(node) for node in nodes)
        else:
            # 2. Virtual Translation Inheritance for empty locales
            lang_code = language.attrib.get("lang", "")
            if lang_code == "en-us":
                continue

            en_locale = language.getparent().find("locale[@lang='en-us']")
            if en_locale is not None:
                for en_node in en_locale.findall("deliverable"):
                    en_id = en_node.get(XML_ID)
                    if not en_id:
                        continue

                    # Create a synthetic xref deliverable pointing to the English blueprint
                    synth_node = etree.Element("deliverable")
                    synth_xref = etree.Element("xref", linkend=en_id)
                    synth_node.append(synth_xref)

                    # Append to the current locale to inherit docset/product ancestors
                    language.append(synth_node)

                    log.info(
                        "Inherited blueprint deliverable '%s' for empty locale '%s'",
                        en_id, lang_code
                    )
                    deliverables.append(Deliverable(synth_node))

    return deliverables
