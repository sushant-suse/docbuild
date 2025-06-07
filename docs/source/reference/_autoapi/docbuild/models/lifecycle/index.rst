docbuild.models.lifecycle
=========================

.. py:module:: docbuild.models.lifecycle

.. autoapi-nested-parse::

   Lifecycle model for docbuild.



Attributes
----------

.. autoapisummary::

   docbuild.models.lifecycle.LifecycleFlag


Classes
-------

.. autoapisummary::

   docbuild.models.lifecycle.BaseLifecycleFlag


Module Contents
---------------

.. py:class:: BaseLifecycleFlag(*args, **kwds)

   Bases: :py:obj:`enum.Flag`


   Base class for LifecycleFlag.


   .. py:method:: from_str(value: str) -> BaseLifecycleFlag
      :classmethod:


      Convert a string to a LifecycleFlag object.

      The string is either a comma or pipe separated list.

      * ``"supported"`` => ``<LifecycleFlag.supported: 2>``
      * ``"supported|beta"`` => ``<LifecycleFlag.supported|beta: 6>``



.. py:data:: LifecycleFlag

   LifecycleFlag is a Flag that represents the lifecycle of a product.


