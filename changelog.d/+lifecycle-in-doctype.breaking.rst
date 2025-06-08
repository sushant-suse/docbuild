Change default of lifecycle in :meth:`~docbuild.models.doctype.Doctype.from_str`

When you called :meth:`~docbuild.models.doctype.Doctype.from_str` with a string that did not contain a lifecycle, it would default to ``supported``.
This may prevent XPaths were you want *all* lifecycles.
This is now changed to ``unknown``.