# from dataclasses import dataclass
from enum import Flag, StrEnum
from typing import Sequence

from pydantic import BaseModel, field_validator

from ..constants import ALLOWED_LANGUAGES, ALLOWED_LIFECYCLES, ALLOWED_PRODUCTS
from .language import LanguageCode


#--- Enums
# Products allows all our SUSE product names, but also "*" (=ALL).
# We only define "ALL" as uppercase to denote a constant, the rest is lowercase.
Product = StrEnum(
    "Product",
    {"ALL": "*"}
    | {item: item.replace("-", "_") for item in ALLOWED_PRODUCTS},
)

# Lifecycle is implemented as a Flag as different states can be combined
# An additional "unknown" state could be used if the state is unknown or not yet
# retrieved.
# TODO: Should we allow weird combination like "supported|unsupported"
LifecycleFlag = Flag(
    "LifecycleFlag",
    {"unknown": 0}
    | {item: (index << 1) for index, item in enumerate(ALLOWED_LIFECYCLES, 1)},
)

# Language allows all the definied languages, but also "*" (=ALL).
# We only define "ALL" as uppercase to denote a constant, the rest is lowercase.
# Language = StrEnum(
#     "Language",
#     # The dict is mapped like "de_de": "de-de"
#     {"ALL": "*"} | {item.replace("-", "_"): item
#                     for item in sorted(ALLOWED_LANGUAGES)},
# )

#--- Models
class Doctype(BaseModel):
    product: Product  # type: ignore
    docset: str
    lifecycle: LifecycleFlag  # type: ignore
    langs: list[LanguageCode]  # type: ignore

    def __str__(self) -> str:
        langs_str = ",".join(lang.language for lang in self.langs)
        return f"{self.product.value}/{self.docset}@{self.lifecycle.value}/{langs_str}"

    def __repr__(self) -> str:
        langs_str = ",".join(lang.language for lang in self.langs)
        return (
            f"{self.__class__.__name__}(product={self.product.value!r}, "
            f"docset={self.docset!r}, "
            f"lifecycle={self.lifecycle.name!r}, "
            f"langs=[{langs_str}]"
            f")"
        )

    @field_validator("product", mode="before")
    def coerce_product(cls, v):
        return v if isinstance(v, Product) else Product(v)

    @field_validator("lifecycle", mode="before")
    def coerce_lifecycle(cls, v):
        return v if isinstance(v, LifecycleFlag) else LifecycleFlag[v]

    @field_validator("langs", mode="before")
    def coerce_langs(cls, v):
        # Allow list of strings or Language enums
        return [lang if isinstance(lang, Language) else
                Language(lang) for lang in v]
