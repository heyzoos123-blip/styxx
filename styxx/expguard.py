# -*- coding: utf-8 -*-
"""styxx.expguard — structural integrity guards for experiment runners (B13).

The 2026-06-08 smoke-artifact lesson (adversarial-curve v3): a smoke-test
result JSON was nearly cited as a real verdict because nothing in the
pipeline made an invalid artifact LOOK invalid. The v4 runner closed that
hole by hand (quarantined filename, script SHA in the JSON, VOID-INSTRUMENT
floor assert). This module makes those guards importable so every future
runner inherits them structurally instead of re-implementing them by
discipline. Discipline is what failed.

Three guards, enforced at the single point where a result becomes a file:

  1. SMOKE QUARANTINE — a smoke run cannot write to a citable filename.
     ``write_result(..., smoke=True)`` forcibly rewrites the output path to
     ``*_SMOKE_INVALID.json`` and stamps ``citable: false`` in the payload,
     regardless of what path the caller supplied.
  2. SCORER SHA — every result JSON carries ``scorer_sha256``, the SHA-256
     of the scorer script that produced it, so a verdict can always be tied
     to the exact code that scored it (hash-before-you-score, RESEARCH_LOOP
     step 2).
  3. INSTRUMENT FLOOR — ``apply_instrument_gate`` compares the reference
     signal to the permutation/chance floor and, below the margin, FORCES
     the program verdict to ``VOID-INSTRUMENT (claim nothing)``, overriding
     whatever verdict the caller computed. A dead instrument cannot emit a
     live claim.

Honest boundary: these guards make invalid artifacts self-describing and
hard to mis-cite. They do not validate the science — a preregistered
kill-gate can still be wrong, and a red-team is still non-optional
(RESEARCH_LOOP step 4). Stdlib only; no styxx imports.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

__all__ = [
    "SMOKE_SUFFIX",
    "VOID_INSTRUMENT",
    "scorer_sha256",
    "quarantine_path",
    "apply_instrument_gate",
    "write_result",
]

# Filename marker for non-citable smoke artifacts. Matches the convention
# locked in PREREG_adversarial_curve_v4_2026_06_08.md §Mandates item 4.
SMOKE_SUFFIX = "_SMOKE_INVALID"

VOID_INSTRUMENT = "VOID-INSTRUMENT (claim nothing)"

# Default minimum (reference_signal − chance_floor) margin, from the v4
# frozen kill-gate's instrument_margin ≥ 0.20 PRE condition.
DEFAULT_MIN_MARGIN = 0.20


def scorer_sha256(script_path: Union[str, Path]) -> str:
    """SHA-256 hex digest of the scorer script's bytes.

    Hash the file that scores, before you score, and carry the hash in the
    result. Raises FileNotFoundError if the script does not exist — a
    result that cannot name its scorer must not be written.
    """
    p = Path(script_path)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def quarantine_path(result_path: Union[str, Path], smoke: bool) -> Path:
    """Return the path a result may legally be written to.

    smoke=False → the path unchanged.
    smoke=True  → ``<stem>_SMOKE_INVALID<suffix>``, idempotently (a path
    already carrying the marker is not double-suffixed).
    """
    p = Path(result_path)
    if not smoke or p.stem.endswith(SMOKE_SUFFIX):
        return p
    return p.with_name(p.stem + SMOKE_SUFFIX + p.suffix)


def apply_instrument_gate(
    payload: Dict[str, Any],
    *,
    reference_signal: float,
    chance_floor: float,
    min_margin: float = DEFAULT_MIN_MARGIN,
    verdict_key: str = "PROGRAM_VERDICT",
) -> Dict[str, Any]:
    """Force VOID-INSTRUMENT when the instrument cannot beat its own floor.

    Records ``instrument_margin``, ``instrument_floor`` and
    ``instrument_reference`` in the payload. If the margin is below
    ``min_margin`` the payload's verdict is OVERWRITTEN with
    ``VOID-INSTRUMENT (claim nothing)`` and the caller's verdict, if any,
    is preserved under ``<verdict_key>_voided`` for the post-mortem.
    Mutates and returns the same dict.
    """
    margin = float(reference_signal) - float(chance_floor)
    payload["instrument_reference"] = float(reference_signal)
    payload["instrument_floor"] = float(chance_floor)
    payload["instrument_margin"] = margin
    if margin < min_margin:
        if verdict_key in payload and payload[verdict_key] != VOID_INSTRUMENT:
            payload[verdict_key + "_voided"] = payload[verdict_key]
        payload[verdict_key] = VOID_INSTRUMENT
    return payload


def write_result(
    result_path: Union[str, Path],
    payload: Dict[str, Any],
    *,
    script_path: Union[str, Path],
    smoke: bool,
    reference_signal: Optional[float] = None,
    chance_floor: Optional[float] = None,
    min_margin: float = DEFAULT_MIN_MARGIN,
    indent: int = 2,
) -> Path:
    """Write an experiment result JSON with all B13 guards applied.

    Stamps ``scorer_sha256`` (of ``script_path``) and ``smoke`` into the
    payload. Smoke runs are quarantined to a ``*_SMOKE_INVALID`` filename
    and stamped ``citable: false``; real runs are stamped ``citable: true``.
    When both ``reference_signal`` and ``chance_floor`` are given, the
    instrument gate is applied before writing. Returns the path actually
    written, which for smoke runs may differ from the one requested.
    """
    out = quarantine_path(result_path, smoke)
    payload["scorer_sha256"] = scorer_sha256(script_path)
    payload["smoke"] = bool(smoke)
    payload["citable"] = not smoke
    if smoke:
        payload.setdefault(
            "smoke_note",
            "smoke artifact: pipeline check only, can never be cited",
        )
    if reference_signal is not None and chance_floor is not None:
        apply_instrument_gate(
            payload,
            reference_signal=reference_signal,
            chance_floor=chance_floor,
            min_margin=min_margin,
        )
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=indent)
    return out
