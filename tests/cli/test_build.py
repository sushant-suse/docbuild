import pytest

from docbuild.models.doctype import Doctype
from docbuild.cli.build import is_subsumed_by, filter_redundant_doctypes


@pytest.mark.parametrize(
    "doctypes",
    [
        ["sles/15-SP6/en-us", "sles/*/en-us"],
        ["sles/15-SP7/en-us", "*/*/en-us"],
    ],
)
def test_is_subsumed_by(doctypes):
    d1, d2 = Doctype.from_str(doctypes[0]), Doctype.from_str(doctypes[1])
    assert is_subsumed_by(d1, d2)
    assert not is_subsumed_by(d2, d1)


@pytest.mark.parametrize(
    "doctypes,expected",
    [
        (["sles/15-SP6/en-us", "sles/*/en-us"], ["sles/*/en-us"]),
        (
            ["sles/15-SP5,15-SP4/en-us,de-de", "sles/*@beta,supported/de-de"],
            ["//en-us,de-de"],
        ),
    ],
)
def test_filter_redundant_doctypes(doctypes, expected):
    result = filter_redundant_doctypes([Doctype.from_str(dt) for dt in doctypes])
    assert result == [Doctype.from_str(dt) for dt in expected]