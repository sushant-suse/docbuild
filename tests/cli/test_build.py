import pytest

from docbuild.models.doctype import Doctype
from docbuild.cli.build import is_subsumed_by, filter_redundant_doctypes, merge_doctypes


@pytest.mark.parametrize(
    "doctypes",
    [
        ["sles/15-SP6/en-us", "sles/*/en-us"],
        ["sles/15-SP7/en-us", "*/*/en-us"],
        ["sles/16-SP0/en-us,de-de", "sles/16-SP0/*"],
        ["sles/15,16/en-us,de-de", "//de-de,en-us"]
    ],
)
def test_is_subsumed_by(doctypes):
    d1, d2 = Doctype.from_str(doctypes[0]), Doctype.from_str(doctypes[1])
    assert is_subsumed_by(d1, d2)
    assert not is_subsumed_by(d2, d1)


@pytest.mark.skip("Not sure if we still need this function")
@pytest.mark.parametrize(
    "doctypes,expected",
    [
        # 1
        (["sles/15-SP6/en-us", "sles/*/en-us"], ["sles/*/en-us"]),
        # 2
        (
            ["sles/15-SP5,15-SP4/de-de", "sles/*@beta,supported/de-de"],
            ["sles/*@beta,supported/de-de"],
        ),
        # 3
        (["sles/15-SP5,15-SP4/*", "sles/15-SP4/en-us"], ["sles/15-SP5,15-SP4/*"]),
    ],
)
def test_filter_redundant_doctypes(doctypes, expected):
    result = filter_redundant_doctypes([Doctype.from_str(dt) for dt in doctypes])
    assert result == [Doctype.from_str(dt) for dt in expected]


@pytest.mark.skip("Needs more thought")
@pytest.mark.parametrize(
    "doctypes,expected",
    [
        # 1 ok
        (["sles/15-SP6/en-us", "sles/*/en-us"], ["sles/*/en-us"]),
        # 2 ok
        (
            ["sles/15-SP5,15-SP4/*", "sles/15-SP4/en-us"],
            ["sles/15-SP4,15-SP5/*", "sles/15-SP4/en-us"],
        ),
        # 3
        (
            [
                "sles/15-SP6,15-SP5/en-us,de-de",
                "sles/*/en-us",
                "smart/network,container/en-us",
            ],
            [
                "sles/15-SP6,15-SP5/de-de",
                "sles/*/en-us",
                "smart/container,network/en-us",
            ],
        ),
        # 4
        (
            [
                "sles/15-SP6,15-SP5/en-us,de-de",
                "sles/15-SP4/zh-cn",
            ],
            ["sles/15-SP5,15-SP6/de-de,en-us", "sles/15-SP4/zh-cn"],
        ),
        # 5
        (
            ["sles/*/en-us", "sles/*/de-de", "sles/16-SP0/zh-cn"],
            ["sles/*/de-de,en-us", "sles/16-SP0/zh-cn"],
        ),
    ],
)
def test_merge_doctypes(doctypes, expected):
    real_dts = [Doctype.from_str(dt) for dt in doctypes]
    assert merge_doctypes(*real_dts) == [Doctype.from_str(dt) for dt in expected]