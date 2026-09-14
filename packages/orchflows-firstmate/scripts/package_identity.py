"""Package identity, installation boundaries, and honest readiness reporting."""

from __future__ import annotations

import json
import os
from pathlib import Path


CORE_NAME = "orchflows-firstmate"
CORE_ALIASES = frozenset((CORE_NAME, "orchflows"))
CATALOG_NAME = "orchflows-firstmate-home"


def home_path(value: str | Path | None = None) -> Path:
    selected = value if value is not None else os.environ.get("ORCHFLOWS_FIRSTMATE_HOME")
    return Path(selected).expanduser().resolve() if selected else (Path.home() / ".orchflows-firstmate").resolve()


def check_setup_home(home: Path) -> None:
    """Refuse overlapping normal Orchflows homes before any installation writes."""
    protected = [(Path.home() / ".orchflows").resolve()]
    if os.environ.get("ORCHFLOWS_HOME"):
        protected.append(Path(os.environ["ORCHFLOWS_HOME"]).expanduser().resolve())
    for normal_home in protected:
        if home.is_relative_to(normal_home) or normal_home.is_relative_to(home):
            raise ValueError(f"FirstMate package home overlaps the normal Orchflows home: {home}")
    if (home / ".local/packages/orchflows").exists():
        raise ValueError(f"Normal Orchflows core already exists in this home: {home}")
    for relative in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
        path = home / relative
        if not path.is_file():
            continue
        try:
            catalog = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            continue  # Setup may repair a damaged catalog in its own home.
        if isinstance(catalog, dict) and catalog.get("name") in {"orchflows-home", "orchflows-local"}:
            raise ValueError(f"Normal Orchflows catalog is protected: {path}")


def readiness() -> dict:
    """Package checks never establish a running controller, binding or worker."""
    return {
        "readiness_scope": "package-only",
        "integration": {
            "status": "experimental-client",
            "execution_ready": False,
            "required_contract": "firstmate-task-group",
            "protocol_version": 1,
            "implemented_scope": "local-readonly-work",
            "target": "FirstMate/Herdr only; Claude Code and Codex CLI worker harnesses",
            "reason": "The experimental client requires an actual FirstMate controller and exact task "
                      "attachment. Package checks do not verify operational runtime or broader workflows.",
        },
    }
