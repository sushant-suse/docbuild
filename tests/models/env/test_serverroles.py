import pytest

from docbuild.models.env.serverroles import ServerRole
from docbuild.constants import SERVER_ROLES


@pytest.mark.parametrize("role", SERVER_ROLES)
def test_serverrole_with_call(role):
    assert ServerRole(role)


@pytest.mark.parametrize("role", SERVER_ROLES)
def test_serverrole_with_predicate(role):
    assert ServerRole[role]
