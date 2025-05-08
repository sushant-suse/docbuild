from dataclasses import dataclass
from typing import Literal
from ..models.doctype import Doctype


@dataclass
class DocBuildContext:
    """The CLI context shared between different subcommands
    """
    # --dry-run
    dry_run: bool = False

    # -v: verbosity level
    verbosity: int = 0

    # --role:
    role: Literal["production", "prod", "testing", "test", "staging", "stage"] = "prod"

    # --configfile: The app's config file
    configfile: str | None = None

    # --config: The accumulated content of all config files ()
    config: dict | None = None

    # --doctypes
    doctypes: list[Doctype] | None = None

    # --debug
    debug: bool = False