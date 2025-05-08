from enum import EnumMeta, StrEnum
from typing import Any

# from pydantic import BaseModel, computed_field

from ..constants import ALLOWED_PRODUCTS


class StrEnumMeta(EnumMeta):
    def __getitem__(cls, key: str) -> Any:
        # Allow both dash and underscore access
        candidates = [key.replace("-", "_"),
                      key.replace("_", "-")
                      ]
        # print(">>> StrEnumMeta.__getitem__", cls, key, candidates)
        for cand in candidates:
            try:
                return super().__getitem__(cand)
            except KeyError:
                continue

        # If no match, raise a clear error
        allowed = ", ".join(repr(k.value) for k in cls)
        raise KeyError(
            f"{key!r} is not a valid member name for {cls.__name__}. "
            f"Allowed values: {allowed}"
        )

class BaseProductEnum(StrEnum, metaclass=StrEnumMeta):
    @classmethod
    def _missing_(cls, value: Any):
        """Custom error for unknown values."""
        allowed = ", ".join(repr(v.value) for v in cls)
        raise ValueError(
            f"{value!r} is not a valid {cls.__name__}. "
            f"Allowed values are: {allowed}"
        )

    # @classmethod
    # def attr(cls, name: str):
    #     """Access enum members using attribute-style names with underscores."""
    #     normalized = name.replace("-", "_")
    #     for member in cls:
    #         if member.value == normalized:
    #             return member
    #     return cls._missing_(name)

# Products allows all our SUSE product names, but also "*" (=ALL).
# We only define "ALL" as uppercase to denote a constant, the rest is lowercase.
# Product name with dashes are replace with underscores.
# You can access "Product.sle_ha", but not "Product.sle-ha"
Product = BaseProductEnum(
    "Product",
    {"ALL": "*"} | {item.replace("-", "_"): item for item in ALLOWED_PRODUCTS},
)
