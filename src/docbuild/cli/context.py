from dataclasses import dataclass
from typing import Literal


@dataclass
class DocBuildContext:
    # --dry-run
    dry_run: bool = False

    # -v: verbosity level
    verbosity: int = 0

    # --role:
    role: Literal["production", "prod", "testing", "test", "staging", "stage"] = "prod"

    # --config:
    config: str | None = None

    # --doctypes
    doctypes: list[str] | None = None

    # --debug
    debug: bool = False