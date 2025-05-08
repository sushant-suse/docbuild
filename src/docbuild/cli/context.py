from dataclasses import dataclass
from typing import Literal
from ..models.doctype import Doctype


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
    doctypes: list[Doctype] | None = None

    # --debug
    debug: bool = False