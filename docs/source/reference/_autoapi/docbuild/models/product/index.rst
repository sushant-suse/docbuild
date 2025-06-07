docbuild.models.product
=======================

.. py:module:: docbuild.models.product

.. autoapi-nested-parse::

   Products for the docbuild application.



Attributes
----------

.. autoapisummary::

   docbuild.models.product.Product


Classes
-------

.. autoapisummary::

   docbuild.models.product.StrEnumMeta
   docbuild.models.product.BaseProductEnum


Module Contents
---------------

.. py:class:: StrEnumMeta

   Bases: :py:obj:`enum.EnumMeta`


   Custom metaclass for StrEnum to allow attribute-style access.


.. py:class:: BaseProductEnum

   Bases: :py:obj:`enum.StrEnum`


   Base class for product enums with custom error handling.


.. py:data:: Product

   A :py:class:`~enum.StrEnum` for the products of the docbuild application.


