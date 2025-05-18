from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
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

    # --configfile: The app's config files
    appconfigfiles: tuple[str | Path, ...] | None = None

    # --config: The accumulated content of all config files ()
    appconfig: dict[str, Any] | None = None

    # --envconfigfiles: The env's config files
    envconfigfiles: tuple[str | Path, ...] | None = None

    # --envconfig: The accumulated content of all env config files
    envconfig: dict[str, Any] | None = None

    # --doctypes
    doctypes: list[Doctype] | None = None

    # --debug
    debug: bool = False