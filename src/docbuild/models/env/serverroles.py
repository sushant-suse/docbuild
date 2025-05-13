from enum import StrEnum
# from typing import Literal, Type

# from pydantic import BaseModel, field_validator, Field

# from ...constants import SERVER_ROLES


# ServerRole = StrEnum(
#     "ServerRole",
#     # Allow lowercase and uppercase names
#     {name: name for name in SERVER_ROLES}
#     | {name.upper(): name for name in SERVER_ROLES},
# )

class ServerRole(StrEnum):
    # production
    PRODUCTION = "production"
    PROD = "prod"
    P = "p"
    production = PRODUCTION
    prod = PROD
    p = P
    # staging
    STAGING = "staging"
    STAGE = "stage"
    S = "s"
    staging = STAGING
    stage = STAGE
    s = S
    # testing
    TESTING = "testing"
    TEST = "test"
    T = "t"
    testing = TESTING
    test = TEST
    t = T
