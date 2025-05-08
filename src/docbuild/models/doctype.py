import re
from typing import ClassVar, Pattern, Self


from pydantic import BaseModel, field_validator

from .language import LanguageCode
from .lifecycle import LifecycleFlag
from .product import Product


#--- Models
class Doctype(BaseModel):
    """A SUSE product

    It contains the following attributes:

    * a product: this is taken from the :class:`Product` class
      which has a limited set of valid products, for example "sles"
      All product names are lowercase acronyms.
    * a docset: a specific release of a product (for example, "15-SP6")
    * a lifecycle: the status of the Doctype, for example "supported"
    * the langs: the languages for a Doctype
    """
    product: Product
    docset: list[str]
    lifecycle: LifecycleFlag
    langs: list[LanguageCode]

    # Pre-compile regex for efficiency
    # The regex contains non-capturing groups on purpose
    # This leads to None in the result if that group isn't matched
    _DOCTYPE_REGEX: ClassVar[Pattern] = re.compile(
        r"^"  # start
        r"(?:([^/@]+|\*))?"  # optional product (group 1)
        r"/(?:([^/@]+|\*))?"  # optional docset (group 2)
        r"(?:@([a-z]+(?:[,|][a-z]+)*))?"  # optional lifecycle (group 3)
        r"/(\*|[\w-]+(?:,[\w-]+)*)$"  # required langs (group 4)
    )

    def __str__(self) -> str:
        langs_str = ",".join(lang.language for lang in self.langs)
        docset_str = ",".join(self.docset)
        return f"{self.product.value}/{docset_str}@{self.lifecycle.name}/{langs_str}"

    def __repr__(self) -> str:
        langs_str = ",".join(lang.language for lang in self.langs)
        docset_str = ",".join(self.docset)
        return (
            f"{self.__class__.__name__}(product={self.product.value!r}, "
            f"docset=[{docset_str}], "
            f"lifecycle={self.lifecycle.name!r}, "
            f"langs=[{langs_str}]"
            f")"
        )

    @field_validator("product", mode="before")
    def coerce_product(cls, value: str|Product):
        """Converts a string into a valid Product"""
        return value if isinstance(value, Product) else Product(value)

    @field_validator("docset", mode="before")
    def coerce_docset(cls, value: str) -> list[str]:
        """Converts a string into a list"""
        #if not isinstance(value, str):
        #    return value
        return value.split(",")

    @field_validator("lifecycle", mode="before")
    def coerce_lifecycle(cls, value: str):
        """Converts a string into a LifecycleFlag"""
        if isinstance(value, str|LifecycleFlag):
            # Delegate it to the LifecycleFlag to deal with
            # the correct parsing and validation
            lifecycles = LifecycleFlag.from_str(value)
            return lifecycles
        elif isinstance(value, LifecycleFlag):
            return value

    @field_validator("langs", mode="before")
    def coerce_langs(cls, value: str|list[str]):
        """Converts a comma-separated string or a list of strings into LanguageCode"""
        # Allow list of strings or Language enums
        if isinstance(value, str):
            value = value.split(",")
        return [lang if isinstance(lang, LanguageCode) else
                LanguageCode(lang) for lang in value]

    @classmethod
    def from_str(cls, doctype_str: str) -> Self:
        """Parse a string that adheres to the doctype format.

        The format has the following syntax::

            [PRODUCT]/[DOCSET][@LIFECYCLE]/LANGS
        """
        match = cls._DOCTYPE_REGEX.match(doctype_str)

        if not match:
            raise ValueError(f"Invalid doctype string format: {doctype_str!r}")

        product, docset, lifecycle, langs = match.groups()
        product = "*" if not product else product
        docset = "*" if not docset else docset
        lifecycle = "supported" if lifecycle is None else lifecycle
        langs = "en-us" if langs is None else langs
        return cls(product=product,
                   docset=docset,
                   lifecycle=lifecycle,
                   langs=langs
        )
