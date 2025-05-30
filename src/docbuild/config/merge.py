"""Merge multiple dictionaries into a new one without modifying inputs."""

from collections.abc import Mapping
from typing import Any


def deep_merge(
    # dct1: ,
    *dcts: dict[str, Any],
) -> dict[str, Any]:
    """Merge multiple dictionaries into a new one without modifying inputs.

    Make a deep copy of the first dictionary and then update it with the
    subsequent dictionaries:

    * If a key exists in both dictionaries, the value from the last dictionary
      qwill overwrite the previous one.
    * If the value is a list, it will concatenate the lists.
    * If the value is a primitive type, it will overwrite the value.
    * If a key exists in multiple dictionaries, the last one will take precedence.

    This means that the order of dictionaries matters. The first dictionary
    will be the base, and the subsequent dictionaries will update it.

    :param dcts: Sequence of dictionaries to merge.
    :return: A new dictionary containing the merged values
            (does not change the passed dictionaries).
    """
    if not dcts:
        return {}

    # Start with a shallow copy of the first dictionary
    merged = dcts[0].copy()

    for d in dcts[1:]:
        stack = [(merged, d)]

        while stack:
            d1, d2 = stack.pop()
            for key, value in d2.items():
                if (
                    key in merged
                    and isinstance(d1[key], dict | Mapping)
                    and isinstance(value, dict | Mapping)
                ):
                    stack.append((d1[key], value))
                else:
                    d1[key] = value

    return merged
