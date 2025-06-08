"""Lifecycle model for docbuild."""

from enum import Flag
import re

from ..constants import ALLOWED_LIFECYCLES


_SEPARATOR = re.compile(r"[|,]")


class BaseLifecycleFlag(Flag):
    """Base class for LifecycleFlag."""

    @classmethod
    def from_str(cls, value: str) -> "BaseLifecycleFlag":
        f"""Convert a string to a LifecycleFlag object.

        The string accepts the values {', '.join(repr(x) for x in ALLOWED_LIFECYCLES)}
        or a combination of them separated by a comma or pipe.
        Addtionally, the class knows the values "UNKNOWN" and "unknown".
        An empty string, "", is equivalent to "UNKNOWN".

        Examples:
        >>> LifecycleFlag.from_str("supported")
        <LifecycleFlag.supported: 2>
        >>> LifecycleFlag.from_str("supported|beta")
        <LifecycleFlag.supported|beta: 6>
        >>> LifecycleFlag.from_str("beta,supported|beta")
        <LifecycleFlag.supported|beta: 6>
        >>> LifecycleFlag.from_str("")
        <LifecycleFlag.unknown: 0>
        """
        try:
            flag = cls(0)  # Start with an empty flag
            parts = [v.strip() for v in _SEPARATOR.split(value) if v.strip()]
            if not parts:
                return cls(0)

            for part_name in parts:
                flag |= cls[part_name]

            return flag

        except KeyError as err:
            allowed = ", ".join(cls.__members__.keys())
            raise ValueError(
                f"Invalid lifecycle name: {err.args[0]!r}. Allowed values: {allowed}",
            ) from err

    def __contains__(self, other: str|Flag) -> bool:
        """Return True if self has at least one of same flags set as other.

        >>> "supported" in Lifecycle.beta
        False
        >>> "supported|beta" in Lifecycle.beta
        True
        """
        if isinstance(other, str):
            item_flag = self.__class__.from_str(other)

        elif isinstance(other, self.__class__):
            item_flag = other

        else:
            return False

        return (self & item_flag) == item_flag


# Lifecycle is implemented as a Flag as different states can be combined
# An additional "unknown" state could be used if the state is unknown or not yet
# retrieved.
# TODO: Should we allow weird combination like "supported|unsupported"
LifecycleFlag = BaseLifecycleFlag(
    "LifecycleFlag",
    {"unknown": 0, "UNKNOWN": 0}
    | {item: (2 << index) for index, item in enumerate(ALLOWED_LIFECYCLES, 0)},
)
"""LifecycleFlag represents the lifecycle of a product."""
