from enum import Flag

from ..constants import ALLOWED_LIFECYCLES


# Lifecycle is implemented as a Flag as different states can be combined
# An additional "unknown" state could be used if the state is unknown or not yet
# retrieved.
# TODO: Should we allow weird combination like "supported|unsupported"
LifecycleFlag = Flag(
    "LifecycleFlag",
    {"unknown": 0}
    | {item: (index << 1) for index, item in enumerate(ALLOWED_LIFECYCLES, 1)},
)
