Refactor ``replace_placeholders()`` function

* Introduce ``PlaceholderResolver`` class to reduce complexity
* Introduce a ``PlaceholderResolutionError``, derived from KeyError
