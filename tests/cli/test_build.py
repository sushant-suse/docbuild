from pathlib import Path
from types import SimpleNamespace

import click
from click import Abort, Command, Context
import pytest

from docbuild.cli.build import (
    filter_redundant_doctypes,
    is_subsumed_by,
    merge_doctypes,
    merge_two_doctypes,
    validate_doctypes,
)
from docbuild.cli.cli import cli
from docbuild.cli.context import DocBuildContext
from docbuild.models.doctype import Doctype


@pytest.mark.parametrize(
    "doctypes",
    [
        ["sles/15-SP6/en-us", "sles/*/en-us"],
        ["sles/15-SP7/en-us", "*/*/en-us"],
        ["sles/16-SP0/en-us,de-de", "sles/16-SP0/*"],
        ["sles/15,16/en-us,de-de", "//de-de,en-us"],
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


def test_validate_doctypes_with_empty_doctypes():
    cmd = Command("dummy_build")
    ctx = Context(cmd)
    ctx.obj = SimpleNamespace()

    result = validate_doctypes(ctx, None, tuple())
    assert not result
    # No ctx.obj.doctypes as this doesn't exist


def test_validate_doctypes_abort(monkeypatch):
    ctx = Context(Command("dummy_build"))
    ctx.obj = SimpleNamespace()

    def raise_for_invalid(s: str) -> DummyDoctype:
        if s.startswith("wrong"):
            raise Abort("is not a valid Product")
        return DummyDoctype(s)

    monkeypatch.setattr(
        "docbuild.cli.build.Doctype.from_str", staticmethod(raise_for_invalid),
    )

    with pytest.raises(Abort, match="is not a valid Product"):
        validate_doctypes(ctx, None, ("wrong/1/en-us",))


def test_validate_doctypes_called_from_build(context, fake_envfile, runner):

    result = runner.invoke(
        cli, ["--role=production", "build", "sles/17/en-us"],
        obj=context,
    )

    assert fake_envfile.mock.call_count == 1
    assert result.exit_code == 0
    # assert "Got sles/17@supported/en-us" in result.output
    assert context.doctypes == [DummyDoctype("sles/17/en-us")]
    assert context.role == "production"


class DummyDoctype:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, DummyDoctype) and self.value == other.value


@pytest.fixture(autouse=True)
def patch_doctype(monkeypatch):
    # Patch Doctype.from_str to return a DummyDoctype for testing
    monkeypatch.setattr(
        "docbuild.cli.build.Doctype",
        type(
            "Doctype",
            (),
            {
                "from_str": staticmethod(lambda s: DummyDoctype(s)),
                "model_fields": {
                    "field": type(
                        "Field", (), {"description": "desc", "examples": ["ex"]},
                    )(),
                },
            },
        ),
    )
    # Patch merge_doctypes to just return the list for simplicity
    monkeypatch.setattr("docbuild.cli.build.merge_doctypes", lambda *args: list(args))


def test_validate_doctypes_empty(ctx):
    context = ctx(SimpleNamespace())
    result = validate_doctypes(context, None, ())
    assert result == []
    assert not hasattr(context.obj, "doctypes") or context.obj.doctypes == []


def test_validate_doctypes_valid(ctx):
    context = ctx(SimpleNamespace())
    doctypes = ("foo/1/en-us", "bar/2/de-de")
    result = validate_doctypes(context, None, doctypes)
    assert result == [DummyDoctype("foo/1/en-us"), DummyDoctype("bar/2/de-de")]
    assert context.obj.doctypes == result


def test_validate_doctypes_invalid(monkeypatch, ctx):
    context = ctx(SimpleNamespace())

    # Patch Doctype.from_str to raise ValidationError
    class DummyValidationError(Exception):
        def errors(self):
            return [{"loc": ["field"], "msg": "bad", "type": "value_error"}]

    monkeypatch.setattr(
        "docbuild.cli.build.Doctype",
        type(
            "Doctype",
            (),
            {
                "from_str": staticmethod(
                    lambda s: (_ for _ in ()).throw(Abort()),
                ),
                "model_fields": {
                    "field": type(
                        "Field", (), {"description": "desc", "examples": ["ex"]},
                    )(),
                },
            },
        ),
    )
    with pytest.raises(click.Abort):
        validate_doctypes(context, None, ("bad/doctype",))


@pytest.mark.parametrize(
    "dt1_str, dt2_str, expected_strs",
    [
        # Different products - should stay separate
        ("sles/15-SP6/en-us", "suma/15-SP6/en-us",
         ["sles/15-SP6/en-us", "suma/15-SP6/en-us"]),

        # Different lifecycle - should stay separate
        ("sles/15-SP6@supported/en-us", "sles/15-SP6@beta/en-us",
            ["sles/15-SP6@supported/en-us", "sles/15-SP6@beta/en-us"]),

        # Different langs - should stay separate
        ("sles/15-SP6/en-us", "sles/15-SP6/de-de",
         ["sles/15-SP6/en-us", "sles/15-SP6/de-de"]),

        # Same everything except docset - should merge
        ("sles/15-SP6/en-us", "sles/15-SP4/en-us", ["sles/15-SP4,15-SP6/en-us"]),

        # Overlapping docsets - should merge and deduplicate
        ("sles/15-SP5,15-SP6/en-us", "sles/15-SP6,16/en-us",
         ["sles/15-SP5,15-SP6,16/en-us"]),

        # Same docset - should return single doctype with same docset
        ("sles/15-SP6/en-us", "sles/15-SP6/en-us", ["sles/15-SP6/en-us"]),
    ],
)
def test_merge_two_doctypes(dt1_str, dt2_str, expected_strs, monkeypatch):
    # Remove the autouse patch to use the real Doctype
    monkeypatch.undo()

    dt1 = Doctype.from_str(dt1_str)
    dt2 = Doctype.from_str(dt2_str)

    result = merge_two_doctypes(dt1, dt2)
    expected = [Doctype.from_str(exp_str) for exp_str in expected_strs]

    # Compare attributes rather than string representation for reliable comparison
    assert len(result) == len(expected)
    for r, e in zip(result, expected, strict=False):
        assert r.product == e.product
        assert r.docset == e.docset
        assert r.lifecycle == e.lifecycle
        assert r.langs == e.langs


@pytest.mark.parametrize(
    "doctypes,expected",
    [
        (tuple(), []),
        (("sles/15-SP6/en-us",), [DummyDoctype("sles/15-SP6/en-us")]),
        (
            ("sles/15-SP6/en-us", "suma/4.3/de-de"),
            [DummyDoctype("sles/15-SP6/en-us"), DummyDoctype("suma/4.3/de-de")],
        ),
    ],
)
def test_validate_doctypes_with_doctypes(ctx, doctypes, expected):
    """Test validate_doctypes with different doctype inputs."""
    context = ctx(SimpleNamespace(doctypes=[]))

    result = validate_doctypes(context, None, doctypes)
    assert result == expected
    assert context.obj.doctypes == expected


def test_validate_doctypes_validation_error(monkeypatch, ctx, capsys):
    """Test that validation errors are properly formatted and displayed."""
    context = ctx(SimpleNamespace(doctypes=[]))

    # Create a mock ValidationError with the structure expected in validate_doctypes
    class MockValidationError(Exception):
        def errors(self):
            return [
                {"loc": ["product"],
                 "msg": "Invalid product name",
                 "type": "value_error"},
            ]

    def mock_from_str(s: str):
        if s.startswith("invalid"):
            raise MockValidationError()
        return DummyDoctype(s)

    # Patch necessary methods
    monkeypatch.setattr("docbuild.cli.build.ValidationError", MockValidationError)
    monkeypatch.setattr("docbuild.cli.build.Doctype.from_str",
                        staticmethod(mock_from_str))
    monkeypatch.setattr("docbuild.cli.build.Doctype.model_fields", {
        "product": type("Field", (), {
            "description": "Product name must be alphanumeric",
            "examples": ["sles", "suma"],
        })(),
    })

    # Test that the function properly aborts and formats error messages
    with pytest.raises(click.Abort):
        validate_doctypes(context, None, ("invalid/product/en-us",))

    captured = capsys.readouterr()
    assert "ERROR in 'product': Invalid product name" in captured.err
    assert "Hint: Product name must be alphanumeric" in captured.out
    assert "Examples: sles, suma" in captured.out


def test_validate_doctypes_merge_called(monkeypatch, ctx):
    """Test that merge_doctypes is called with the correct arguments."""
    context = ctx(SimpleNamespace())
    doctypes = ("sles/15/en-us", "suma/4.3/de-de")

    # Track merge_doctypes calls
    mock_merge_called_with = []

    def mock_merge(*args):
        nonlocal mock_merge_called_with
        mock_merge_called_with = args
        return list(args)

    monkeypatch.setattr("docbuild.cli.build.merge_doctypes", mock_merge)

    validate_doctypes(context, None, doctypes)

    # Verify merge_doctypes was called with both doctypes
    assert len(mock_merge_called_with) == 2
    assert all(isinstance(dt, DummyDoctype) for dt in mock_merge_called_with)
    assert [dt.value for dt in mock_merge_called_with] == [
        "sles/15/en-us", "suma/4.3/de-de",
    ]


def test_validate_doctypes_echo_outputs(ctx, capsys):
    """Test the echo statements in validate_doctypes."""
    context = ctx(SimpleNamespace())
    validate_doctypes(context, None, ("sles/15/en-us",))

    captured = capsys.readouterr()
    assert "validate_set" in captured.out
    assert "Got " in captured.out



