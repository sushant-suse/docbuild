from pydantic import BaseModel, field_validator

from .language import LanguageCode
from .lifecycle import LifecycleFlag
from .product import Product


#--- Models
class Doctype(BaseModel):
    product: Product
    docset: str
    lifecycle: LifecycleFlag
    langs: list[LanguageCode]

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
    def coerce_product(cls, value):
        return value if isinstance(value, Product) else Product(value)

    @field_validator("lifecycle", mode="before")
    def coerce_lifecycle(cls, value):
        return value if isinstance(value, LifecycleFlag) else LifecycleFlag[value]

    @field_validator("langs", mode="before")
    def coerce_langs(cls, value):
        # Allow list of strings or Language enums
        return [lang if isinstance(lang, LanguageCode) else
                LanguageCode(lang) for lang in value]
