docbuild.cli.cli
================

.. py:module:: docbuild.cli.cli

.. autoapi-nested-parse::

   Main CLI tool for document operations.



Functions
---------

.. autoapisummary::

   docbuild.cli.cli.cli


Module Contents
---------------

.. py:function:: cli(ctx: click.Context, verbose: int, dry_run: bool, debug: bool, app_config: pathlib.Path, env_config: pathlib.Path, **kwargs: dict) -> None

   Acts as a main entry point for CLI tool.

   :param ctx: The Click context object.
   :param verbose: The verbosity level.
   :param dry_run: If set, just pretend to run the command without making any changes.
   :param debug: If set, enable debug mode.
   :param app_config: Filename to the application TOML config file.
   :param env_config: Filename to a environment's TOML config file.
   :param kwargs: Additional keyword arguments.


