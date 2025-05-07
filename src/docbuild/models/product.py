from enum import StrEnum

from ..constants import ALLOWED_PRODUCTS


# Products allows all our SUSE product names, but also "*" (=ALL).
# We only define "ALL" as uppercase to denote a constant, the rest is lowercase.
Product = StrEnum(
    "Product",
    {"ALL": "*"} | {item: item.replace("-", "_") for item in ALLOWED_PRODUCTS},
)
