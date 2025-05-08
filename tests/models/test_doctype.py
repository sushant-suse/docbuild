import pytest

# from docbuild.constants import ALLOWED_LIFECYCLES
from docbuild.models.doctype import Doctype
from docbuild.models.language import LanguageCode
from docbuild.models.lifecycle import LifecycleFlag
from docbuild.models.product import Product


def test_valid_doctype():
    doctype = Doctype(product="sles",
                      docset="15-SP6",
                      lifecycle="supported",
                      langs=["en-us"])
    assert doctype.product == Product.sles
    assert doctype.docset == ["15-SP6"]
    assert doctype.lifecycle == LifecycleFlag.supported
    assert doctype.langs == [LanguageCode("en-us")]


def test_str_in_doctype():
    doctype = Doctype(
        product="sles", docset="15-SP6", lifecycle="supported", langs=["en-us"]
    )
    assert str(doctype) == "sles/15-SP6@supported/en-us"


def test_repr_in_doctype():
    doctype = Doctype(
        product="sles", docset="15-SP6", lifecycle="supported", langs=["en-us"]
    )
    assert (
        repr(doctype)
        == "Doctype(product='sles', docset=[15-SP6], lifecycle='supported', langs=[en-us])"
    )


def test_string_langs_in_doctype():
    doctype = Doctype(
        product="sles", docset="15-SP6", lifecycle="supported", langs="en-us"
    )
    assert doctype.langs == [LanguageCode("en-us")]


def test_multiplestrings_langs_in_doctype():
    doctype = Doctype(
        product="sles", docset="15-SP6", lifecycle="supported", langs="en-us,de-de"
    )
    assert doctype.langs == [LanguageCode("en-us"), LanguageCode("de-de")]


@pytest.mark.parametrize(
    "string,expected",
    [
        (
            "sles/15-SP6/en-us",
            (
                Product.sles,
                ["15-SP6"],
                LifecycleFlag.supported,
                [LanguageCode("en-us")],
            ),
        ),
        (
            "sles/15-SP5,15-SP6/en-us",
            (
                Product.sles,
                ["15-SP5", "15-SP6"],
                LifecycleFlag.supported,
                [LanguageCode("en-us")],
            ),
        ),
        (
            "//en-us",
            (Product.ALL, ["*"], LifecycleFlag.supported, [LanguageCode("en-us")]),
        ),
        (
            "*//en-us",
            (Product.ALL, ["*"], LifecycleFlag.supported, [LanguageCode("en-us")]),
        ),
        (
            "/*/en-us",
            (Product.ALL, ["*"], LifecycleFlag.supported, [LanguageCode("en-us")]),
        ),
        (
            "*/*/en-us",
            (Product.ALL, ["*"], LifecycleFlag.supported, [LanguageCode("en-us")]),
        ),
        (
            "*/@beta/en-us",
            (Product.ALL, ["*"], LifecycleFlag.beta, [LanguageCode("en-us")]),
        ),
        (
            "*/*@beta/en-us",
            (Product.ALL, ["*"], LifecycleFlag.beta, [LanguageCode("en-us")]),
        ),
        (
            "sles/*@beta/en-us",
            (Product.sles, ["*"], LifecycleFlag.beta, [LanguageCode("en-us")]),
        ),
    ],
)
def test_valid_string_from_string(string, expected):
    doctype = Doctype.from_str(string)
    product, docset, lifecycle, langs = expected
    assert doctype.product == product
    assert doctype.docset == docset
    assert doctype.lifecycle == lifecycle
    assert doctype.langs == langs


def test_invalid_string_from_string():
    with pytest.raises(ValueError):
        Doctype.from_str("nonsense")