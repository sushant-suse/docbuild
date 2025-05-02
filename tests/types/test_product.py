import pytest

from docbuild.types.product import Product, VALID_PRODUCTS
from pydantic import ValidationError


def test_product_name_is_avilable():
    p = Product(productid="sles")
    assert p.name


def test_productid_is_required():
    with pytest.raises(ValidationError):
        Product()  # type: ignore