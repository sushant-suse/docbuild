"""Module for defining the Doctype model."""

import re
from re import Pattern
from typing import ClassVar, Self

from pydantic import BaseModel, Field, field_validator

from .language import LanguageCode
from .lifecycle import BaseLifecycleFlag, LifecycleFlag
from .product import Product


#--- Models
class Doctype(BaseModel):
    """A "doctype" that comprises of a product, docset, lifecycle, and language.

    >>> Doctype.from_str("sles/15-SP6@supported/en-us,de-de")
    Doctype(product=<Product.SLES: 'sles'>, docset=['15-SP6'], \
    lifecycle=<LifecycleFlag.SUPPORTED: 'supported'>, \
    langs=[LanguageCode(language='en-us'), LanguageCode(language='de-de')])
    """

    # __init__.__doc__ = """Create a new Doctype instance.

    # :param product: A SUSE product, e.g. 'sles', 'smart'.
    # :param docset: A specific release or version of a product.
    # :param lifecycle: The state of the Doctype, e.g. 'supported', 'beta'.
    # :param langs: A natural language, e.g. 'en-us', 'de-de'.

    # :raises pydantic_core.ValidationError: if the input values are invalid.
    # """   # type: ignore

    product: Product = Field(
            title="A SUSE product",
            description="A SUSE product is a lowercase acronym.",
            examples=["sles", "smart"],
    )
    """A SUSE product is a lowercase acronym"""

    docset: list[str] = Field(
            title="A specific 'docset' of a product",
            description=(
                "A specific release or version of a product. "
                "Values can be combined using commas. "
                "After validation, docsets are sorted."
            ),
            examples=["15-SP6", "systems-management"],
    )
    """A specific 'docset' of a product (usually a release or version)"""

    lifecycle: LifecycleFlag = Field(
            title="The state of the Doctype",
            description=(
                "One or more lifecycle states that indicate the "
                "support or development. "
                "Values can be combined using commas or pipes."
            ),
            examples=["supported", "beta", "unsupported"],
    )
    """The state  (supported, beta, etc.) of the Doctype"""

    langs: list[LanguageCode] = Field(
            title="A natural language",
            description=(
                "The natural language containing language and country. "
                "After validation, langs are sorted"
            ),
            examples=["en-us", "de-de"],
    )
    """A natural language containing language and country"""

    # Pre-compile regex for efficiency
    # The regex contains non-capturing groups on purpose
    # This leads to None in the result if that group isn't matched
    _DOCTYPE_REGEX: ClassVar[Pattern] = re.compile(
        r"^"  # start
        r"(?:([^/@]+|\*))?"  # optional product (group 1)
        r"/(?:([^/@]+|\*))?"  # optional docset (group 2)
        r"(?:@([a-z]+(?:[,|][a-z]+)*))?"  # optional lifecycle (group 3)
        r"/(\*|[\w-]+(?:,[\w-]+)*)$",  # required langs (group 4)
    )

    # dunder methods
    def __eq__(self, other: object) -> bool:
        """Check equality with another Doctype, ignoring order in docset/langs."""
        if not isinstance(other, Doctype):
            return NotImplemented

        return (
            self.product == other.product and
            self.lifecycle == other.lifecycle and
            set(self.docset) == set(other.docset) and
            set(self.langs) == set(other.langs)
        )

    def __lt__(self, other: object) -> bool:
        """Check if this Doctype is less than another Doctype."""
        if not isinstance(other, Doctype):
            return NotImplemented

        # Define sort priority: product > lifecycle > docset > langs
        return (
            self.product,
            self.lifecycle,
            self.docset, # we rely on a sorted docset
            self.langs,  # we rely on sorted languages
        ) < (other.product, other.lifecycle, other.docset, other.langs)

    def __str__(self) -> str:
        """Implement str(self)."""
        langs_str = ",".join(lang.language for lang in self.langs)
        docset_str = ",".join(self.docset)
        return f"{self.product.value}/{docset_str}@{self.lifecycle.name}/{langs_str}"

    def __repr__(self) -> str:
        """Implement repr(self)."""
        langs_str = ",".join(lang.language for lang in self.langs)
        docset_str = ",".join(self.docset)
        return (
            f"{self.__class__.__name__}(product={self.product.value!r}, "
            f"docset=[{docset_str}], "
            f"lifecycle={self.lifecycle.name!r}, "
            f"langs=[{langs_str}]"
            f")"
        )

    def __contains__(self, other: "Doctype") -> bool:
        """Return if bool(other in self).

        Every part of a Doctype is compared element-wise.
        """
        if not isinstance(other, Doctype):
            return NotImplemented

        return all(
            [
                self.product == other.product or self.product == Product.ALL,
                set(other.docset).issubset(self.docset) or "*" in self.docset,
                other.lifecycle in self.lifecycle,
                set(other.langs).issubset(self.langs) or "*" in self.langs,
            ],
        )

    def __hash__(self) -> int:
        """Implement hash(self)."""
        return hash(
            (
                self.product,
                tuple(self.docset),
                tuple(self.langs),
            ),
        )

    # Validators
    @field_validator("product", mode="before")
    @classmethod
    def coerce_product(cls, value: str|Product) -> Product:
        """Convert a string into a valid Product."""
        return value if isinstance(value, Product) else Product(value)

    @field_validator("docset", mode="before")
    @classmethod
    def coerce_docset(cls, value: str | list[str]) -> list[str]:
        """Convert a string into a list."""
        return sorted(value.split(",")) if isinstance(value, str) else sorted(value)

    @field_validator("lifecycle", mode="before")
    @classmethod
    def coerce_lifecycle(
        cls, value: str | LifecycleFlag) -> BaseLifecycleFlag:
        """Convert a string into a LifecycleFlag."""
        # value = "" if value is None else value
        if isinstance(value, str):
            # Delegate it to the LifecycleFlag to deal with
            # the correct parsing and validation
            lifecycles = LifecycleFlag.from_str(value)
            return lifecycles
        return LifecycleFlag(value)

    @field_validator("langs", mode="before")
    @classmethod
    def coerce_langs(cls, value: str|list[str|LanguageCode]) -> list[LanguageCode]:
        """Convert a comma-separated string or a list of strings into LanguageCode."""
        # Allow list of strings or Language enums
        if isinstance(value, str):
            value = sorted(value.split(","))
        return sorted([lang if isinstance(lang, LanguageCode) else
                LanguageCode(lang) for lang in value])

    @classmethod
    def from_str(cls, doctype_str: str) -> Self:
        """Parse a string that adheres to the doctype format.

        The format has the following syntax::

            [PRODUCT]/[DOCSETS][@LIFECYCLES]/LANGS

        Plural means you can have one or more items:

        * ``PRODUCT``: a lowercase acronym of a SUSE product, e.g. ``sles``
        * ``DOCSETS``: separated by comma
        * ``LIFECYCLES``: separated by comma or pipe
        * ``LANGS``: separated by comma
        """
        match = cls._DOCTYPE_REGEX.match(doctype_str)

        if not match:
            raise ValueError(f"Invalid doctype string format: {doctype_str!r}")

        product, docset, lifecycle, langs = match.groups()
        product = "*" if not product else product
        docset = "*" if not docset else docset
        lifecycle = "unknown" if lifecycle is None else lifecycle
        langs = "en-us" if langs is None else langs
        return cls(product=product,
                   docset=docset,
                   lifecycle=lifecycle,
                   langs=langs,
        )
