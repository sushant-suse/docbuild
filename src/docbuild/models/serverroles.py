"""Server roles for the docbuild application."""

from enum import StrEnum

# from typing import Literal, Type
# from pydantic import BaseModel, field_validator, Field
# from ...constants import SERVER_ROLES
#
# ServerRole = StrEnum(
#     "ServerRole",
#     # Allow lowercase and uppercase names
#     {name: name for name in SERVER_ROLES}
#     | {name.upper(): name for name in SERVER_ROLES},
# )


class ServerRole(StrEnum):
    """The server role."""

    # production
    PRODUCTION = 'production'
    """Server is in production mode, serving live traffic."""
    PROD = PRODUCTION
    P = PRODUCTION
    production = PRODUCTION
    prod = PRODUCTION
    p = PRODUCTION
    # staging
    STAGING = 'staging'
    """Server is in staging mode, used for testing before production."""
    STAGE = STAGING
    S = STAGING
    staging = STAGING
    stage = STAGING
    s = STAGING
    # testing
    TESTING = 'testing'
    """Server is in testing mode, used for development and QA."""
    TEST = TESTING
    T = TESTING
    testing = TESTING
    test = TESTING
    t = TESTING
