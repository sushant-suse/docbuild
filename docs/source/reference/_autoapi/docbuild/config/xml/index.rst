docbuild.config.xml
===================

.. py:module:: docbuild.config.xml

.. autoapi-nested-parse::

   Module for handling XML configuration files



Functions
---------

.. autoapisummary::

   docbuild.config.xml.list_all_deliverables


Package Contents
----------------

.. py:function:: list_all_deliverables(tree: lxml.etree._Element | lxml.etree._ElementTree, lifecycle: collections.abc.Sequence[str] | None = None, docsuites: collections.abc.Sequence[str] | None = None) -> Generator[lxml.etree._Element, None, None]

   Generator to list all deliverables from the stitched Docserv config

   :param tree: the XML tree from the stitched Docserv config
   :param lifecycle: The lifecycle(s) to taken care of
   :param docsuite: a sequence of "docsuite" identifiers. Each identifier
        is a string in the format ``product/docset/lang``.
   :yield: the `<deliverable>` node that matches the criteria


