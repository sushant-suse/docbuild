from pydantic import BaseModel, Field, field_validator

from ..constants import VALID_PRODUCTS


# categories: list[CategoryType]
# descriptions: list[DescriptionType]
# schemaversion: Optional[str]
# docsets: list[Docset] = Field(
#    title="List of docsets",
#    description="Docsets of the product",
# )
class Product(BaseModel):
    """A product is a collection of docsets"""
    # -- Required fields
    productid: str  = Field(
        title="Product ID",
        description="The unique identifier for this product",
    )

    # -- Calculated fields
    name: str|None = Field(
        default=None,
        init=False,
        title="Full product name"
    )

    # -- Optional fields
    enabled: bool = Field(
        default=True,
        title="Product enabled",
        description="If True, the product is enabled",
        repr=False,
    )
    sortname: str | None = Field(
        default=None,
        title="Product sort name",
        description="The sort name of the product",
        repr=False,
    )
    maintainers: list[str] | None = Field(
        default=None,
        title="Product maintainers",
        description="The maintainers of the product",
        repr=False,
    )

    # -- Validators
    @field_validator("productid")
    @classmethod
    def validate_productid(cls, value):
        if value not in VALID_PRODUCTS:
            raise ValueError(
                f"Invalid productid {value}. "
                f"Must be one of {VALID_PRODUCTS}"
            )
        return value

    def model_post_init(self, __context) -> None:
        self.name = VALID_PRODUCTS[self.productid]