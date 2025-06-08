docbuild.models.lifecycle.BaseLifecycleFlag
===========================================

.. py:class:: docbuild.models.lifecycle.BaseLifecycleFlag(*args, **kwds)

   Bases: :py:obj:`enum.Flag`

   .. autoapi-inheritance-diagram:: docbuild.models.lifecycle.BaseLifecycleFlag
      :parts: 1


   Base class for LifecycleFlag.


   .. py:method:: from_str(value: str) -> BaseLifecycleFlag
      :classmethod:


      Convert a string to a LifecycleFlag object.

      The string is either a comma or pipe separated list.

      * ``"supported"`` => ``<LifecycleFlag.supported: 2>``
      * ``"supported|beta"`` => ``<LifecycleFlag.supported|beta: 6>``



   .. py:method:: __contains__(other: str | enum.Flag) -> bool

      Return True if self has at least one of same flags set as other.

      >>> "supported" in Lifecycle.beta
      False
      >>> "supported|beta" in Lifecycle.beta
      True


