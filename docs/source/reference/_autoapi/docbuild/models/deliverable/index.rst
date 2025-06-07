docbuild.models.deliverable
===========================

.. py:module:: docbuild.models.deliverable

.. autoapi-nested-parse::

   Module for defining the Deliverable model.



Classes
-------

.. autoapisummary::

   docbuild.models.deliverable.Deliverable


Module Contents
---------------

.. py:class:: Deliverable

   A class to represent a deliverable.

   Usually called with a ``<deliverable>`` node from the XML
   configuration file. It contains information about the product,
   docset, language, branch, and other metadata related to the
   deliverable.


   .. py:property:: productid
      :type: str


      Return the product ID



   .. py:property:: docsetid
      :type: str


      Return the docset ID



   .. py:property:: lang
      :type: str


      Returns the language and country code (e.g., 'en-us')



   .. py:property:: language
      :type: str


      Returns only the language (e.g., 'en')



   .. py:property:: product_docset
      :type: str


      Returns product and docset
              



   .. py:property:: pdlang
      :type: str


      Product, docset, and language



   .. py:property:: pdlangdc
      :type: str


      Product, docset, language and DC filename



   .. py:property:: full_id
      :type: str


      Returns the full ID of the deliverable



   .. py:property:: lang_is_default
      :type: bool


      Checks if the language is the default language



   .. py:property:: docsuite
      :type: str


      Returns the product, docset, language and the DC filename



   .. py:property:: branch
      :type: str


      Returns the branch where to find the deliverable



   .. py:property:: subdir
      :type: str


      Returns the subdirectory inside the repository



   .. py:property:: git
      :type: str


      Returns the git repository



   .. py:property:: dcfile
      :type: str


      Returns the DC filename



   .. py:property:: basefile
      :type: str


      Returns the DC filename without the DC prefix



   .. py:property:: format
      :type: dict[Literal['html', 'single-html', 'pdf', 'epub'], bool]


      Returns the formats of the deliverable



   .. py:property:: node
      :type: lxml.etree._Element


      Returns the node of the deliverable



   .. py:property:: productname
      :type: str


      Returns the product name



   .. py:property:: acronym
      :type: str


      Returns the product acronym



   .. py:property:: version
      :type: str


      Returns the version of the docset



   .. py:property:: lifecycle
      :type: str


      Returns the lifecycle of the docset



   .. py:property:: relpath
      :type: str


      Returns the relative path of the deliverable



   .. py:property:: repo_path
      :type: pathlib.Path


      Returns the "slug" path of the repository



   .. py:property:: zip_path
      :type: str


      Returns the path to the ZIP file



   .. py:property:: html_path
      :type: str


      Returns the path to the HTML directory.



   .. py:property:: singlehtml_path
      :type: str


      Returns the path to the single HTML directory



   .. py:property:: pdf_path
      :type: str


      Returns the path to the PDF file



   .. py:property:: product_node
      :type: lxml.etree._Element


      Returns the product node of the deliverable



   .. py:property:: docset_node
      :type: lxml.etree._Element


      Returns the docset node of the deliverable



   .. py:property:: metafile
      :type: str | None


      Returns the metadata file



   .. py:property:: meta
      :type: docbuild.models.metadata.Metadata | None


      Returns the metadata object of the deliverable



   .. py:method:: to_dict() -> dict
      :abstractmethod:


      Return the deliverable as a JSON object



   .. py:method:: make_safe_name(name: str) -> str
      :staticmethod:


      Make a name safe for use in a filename or directory



