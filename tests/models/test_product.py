import pytest

from docbuild.constants import ALLOWED_PRODUCTS
from docbuild.models.product import Product


@pytest.mark.parametrize("product", ALLOWED_PRODUCTS)
def test_valid_product(product):
    instance = getattr(Product, product)
    assert instance.name == product


def test_wildcard_product():
    instance = Product.ALL
    assert instance.name == "ALL"
    assert instance.value == "*"