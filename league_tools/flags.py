"""Run the detectors over a match's demo once, and keep its flags beside its result.

The detectors (``league_tools/detectors/``) read nothing but the demo. This
module is the part that touches files: it finds them, hashes their source
and keeps each match's flags in the local result cache as
``<key>.flags-<hash>.json``, so a new or changed detector computes the flags
again, and nothing else does. Flags stay on this machine: computing them
plays no game, so another machine computes its own.
"""

from __future__ import annotations

import functools
import hashlib
import importlib
import json
import os
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import Any

from . import detectors, digest
from .detectors import Flag
from .paths import CACHE

PACKAGE = Path(detectors.__file__).parent


@functools.cache
def registry() -> tuple[ModuleType, ...]:
    """Every detector, by its module's name: the package's modules whose name doesn't start with ``_``.

    Raises:
        ValueError: A detector has no ``KIND``, no ``detect`` or no docstring,
            or two share a ``KIND``.
    """
    found = []
    for module_info in sorted(pkgutil.iter_modules([str(PACKAGE)]), key=lambda info: info.name):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{detectors.__name__}.{module_info.name}")
        if not isinstance(getattr(module, "KIND", None), str) or not callable(getattr(module, "detect", None)):
            raise ValueError(f"detector {module_info.name} needs a KIND and a detect(demo)")
        if not (module.__doc__ or "").strip():
            raise ValueError(f"detector {module_info.name} needs a docstring: the mistake and its lesson")
        found.append(module)
    kinds = [module.KIND for module in found]
    repeated = sorted({kind for kind in kinds if kinds.count(kind) > 1})
    if repeated:
        raise ValueError(f"more than one detector has the kind {', '.join(repeated)}")
    return tuple(found)


def kinds() -> list[str]:
    """The kinds of every detector, in the registry's order."""
    return [module.KIND for module in registry()]


def run_all(demo: dict[str, Any]) -> list[Flag]:
    """Every detector's flags on one demo, by kind, then team, then turn."""
    flags = [flag for module in registry() for flag in module.detect(demo)]
    return sorted(flags, key=lambda flag: (flag.kind, flag.team, flag.turns))


@functools.cache
def detectors_hash() -> str:
    """A hash of every source file of the detectors' package: a new or changed detector changes it."""
    digest_of = hashlib.sha256()
    for path in sorted(PACKAGE.glob("*.py")):
        digest_of.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest_of.hexdigest()


def flags_path(key: str) -> Path:
    """Where a match's flags are kept, under the detectors' hash."""
    return CACHE / f"{key}.flags-{detectors_hash()[:12]}.json"


def flags_for(result: dict[str, Any]) -> list[Flag]:
    """A played match's flags: read from the cache, or computed from its demo once and kept there.

    Args:
        result: A match's result as a tournament returns it, with its ``id``
            (the match key) and its ``demo``.
    """
    path = flags_path(result["id"])
    if path.is_file():
        return [Flag.from_dict(entry) for entry in json.loads(path.read_text(encoding="utf-8"))]
    flags = run_all(digest.load_demo(Path(result["demo"])))
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f".{path.name}.{os.getpid()}")
    partial.write_text(json.dumps([flag.as_dict() for flag in flags]), encoding="utf-8")
    os.replace(partial, path)
    return flags
