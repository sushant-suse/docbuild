

from collections.abc import Mapping
from typing import Any


def deep_merge(
    dct1: dict[str, Any], *dcts: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Create a deep copy of dct1 and merge it with dcts[0], dcts[1], ...
    into a new dict.

    Later dict values overwriting earlier ones.
    Requires at least one dictionary argument.
    Returns a new merged dictionary without modifying inputs.

    :param dict1: The first dictionary to merge into.
    :param dicts: Additional dictionaries to merge into the first one.
    :return: A new dictionary containing the merged values
            (does not change the passed dictionaries).
    """

    # Start with a shallow copy of the first dictionary
    merged = dct1.copy()

    for d in dcts:
        stack = [(merged, d)]

        while stack:
            d1, d2 = stack.pop()
            for key, value in d2.items():
                if (
                    key in merged
                    and isinstance(d1[key], (dict, Mapping))
                    and isinstance(value, (dict, Mapping))
                ):
                    stack.append((d1[key], value))
                else:
                    d1[key] = value

    return merged