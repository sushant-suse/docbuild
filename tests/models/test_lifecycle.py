import pytest

from docbuild.constants import ALLOWED_LIFECYCLES
from docbuild.models.lifecycle import LifecycleFlag


@pytest.mark.parametrize("lifecycle", ALLOWED_LIFECYCLES)
def test_valid_lifecycles(lifecycle):
    instance = getattr(LifecycleFlag, lifecycle)
    assert instance.name == lifecycle


def test_unknown_lifecycle():
    instance = getattr(LifecycleFlag, "unknown")
    assert instance.name == "unknown"
    assert instance.value == 0