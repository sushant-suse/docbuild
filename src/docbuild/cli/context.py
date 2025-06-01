"""Context for the docbuild CLI commands."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..models.doctype import Doctype
from ..models.serverroles import ServerRole


@dataclass
class DocBuildContext:
    """The CLI context shared between different subcommands."""

    # --dry-run
    dry_run: bool = False

    # -v: verbosity level
    verbose: int = 0

    # --role: obsolete
    # role: ServerRole | None = None  # ServerRole.production

    # --configfile: The app's config files
    appconfigfiles: tuple[str | Path, ...] | None = None

    # Internal flag to indicate if the app's config was loaded from defaults
    appconfig_from_defaults: bool = False

    # --config: The accumulated content of all config files ()
    appconfig: dict[str, Any] | None = None

    # --envconfigfiles: The env's config files
    envconfigfiles: tuple[str | Path, ...] | None = None

    # Internal flag to indicate if the env's config was loaded from defaults
    envconfig_from_defaults: bool = False

    # --envconfig: The accumulated content of all env config files
    envconfig: dict[str, Any] | None = None

    # --doctypes
    doctypes: list[Doctype] | None = None

    # --debug
    debug: bool = False
