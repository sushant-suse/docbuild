##########
Change Log
##########

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


Changes for the upcoming release can be found in the
`"changelog.d" directory <https://github.com/tomschr/docbuild/tree/main/changelog.d>`_ of the repository.

..
   Do *NOT* add changelog entries here!

   This changelog is managed by towncrier and is compiled at release time.

   See https://python-semver.rtd.io/en/latest/development.html#changelog
   for details.

.. towncrier release notes start

Version 0.8.0
=============

Breaking Changes
----------------

- Change default of lifecycle in :meth:`~docbuild.models.doctype.Doctype.from_str`

  When you called :meth:`~docbuild.models.doctype.Doctype.from_str` with a string that did not contain a lifecycle, it would default to ``supported``.
  This may prevent XPaths were you want *all* lifecycles.
  This is now changed to ``unknown``.


Features
--------

- Add new list_all_deliverables for XML files

  Generator to yield all deliverables in XML format.
- Implement logging

  Add new functions:

  * :func:`~docbuild.logging.create_base_log_dir`: Create the base log directory if it doesn't exist.
  * :func:`~docbuild.logging.setup_logging`: Set up logging for the application.
  * :func:`~docbuild.logging.get_effective_level`: Return a valid log level, clamped safely.

  The `setup_logging` sets different loggers for the app itself, for Jinja,
  XPath, and Git.


Version 0.7.0
=============

Improved Documentation
----------------------

- Add first docbuild documentation

  * Add sphinx, sphinx-click, sphinx-autoapi, sphinx-copybutton,
    sphinx-autodoc-typehints, and pydata-sphinx-theme to "docs"
    group (pyproject.toml)
  * Add missing ipython in "repl" group
  * Distinguish between a User Guide, Developer Guide, and API Reference
  * Use sphinx-click to "self-document" the docbuild script
  * Use sphinx-autoapi to autogenerate API documentation
  * Fix docstrings in modules, classes etc. to adhere to
    documentation standard


Features
--------

- Implement Deliverable & Metadata classes

  * Deliverable contains an ``etree._Element`` class and represents
    an interface to extract important values from the XML config
  * Metadata is a dataclass that reads the output of "daps metadata" from a file
  * Add test files for each class
  * Add utility function :func:`~docbuild.utils.convert.convert2bool`


Infrastructure
--------------

- Add missing license file (GPL-3.0-or-later)
- Add py.typed in project and pyproject.toml
- Add towncrier to create summarised news files
- Rename ``docbuild.cli.config.{app,env}``

  The names are similar to other files. To make it easier to distinguish,
  these are renamed:

  * ``docbuild.cli.config.{app => application}``
  * ``docbuild.cli.config.{env => environment}``
  * Do the same with the test files
- Update :file:`.gitignore` for :file:`.ipython`


Removed Features
----------------

- Remove tool.setuptools.packages.find

----