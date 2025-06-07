docbuild.config.app
===================

.. py:module:: docbuild.config.app

.. autoapi-nested-parse::

   Application configuration handling.



Attributes
----------

.. autoapisummary::

   docbuild.config.app.Container
   docbuild.config.app.StackItem
   docbuild.config.app.MAX_RECURSION_DEPTH


Functions
---------

.. autoapisummary::

   docbuild.config.app.replace_placeholders


Module Contents
---------------

.. py:data:: Container

   A dictionary or list container for any configuration data.


.. py:data:: StackItem

   A tuple representing a stack item for placeholder resolution.


.. py:data:: MAX_RECURSION_DEPTH
   :type:  int
   :value: 10


   The maximum recursion depth for placeholder replacement.


.. py:function:: replace_placeholders(config: Container, max_recursion_depth: int = MAX_RECURSION_DEPTH) -> Container

   Replace placeholder values in a nested dictionary structure.

   * ``{foo}`` resolves from the current section.
   * ``{a.b.c}`` resolves deeply from the config.
   * ``{{foo}}`` escapes to literal ``{foo}``.

   :param config: The loaded configuration dictionary.
   :return: A new dictionary with placeholders replaced.
   :raises KeyError: If a placeholder cannot be resolved.


