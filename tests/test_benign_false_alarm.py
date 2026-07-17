# -*- coding: utf-8 -*-
"""Pipeline-level benign-text false-alarm guard.

The per-instrument guards lock each axis; this one locks what an agent
actually experiences — the full `styxx.preflight()` gate decision — across the
diverse benign-text classes surfaced over the 2026-06-15 false-alarm work:
confident factual statements (overconfidence-saturated), math/directions/legal
uses of "right", "your code is correct" (possessive + ambiguous), neutral
analysis containing "compelling", hedged uncertainty, and direct disagreement.

A well-behaved agent producing any of these should NOT be told to revise.
This is the durable cross-instrument regression: if any single instrument
starts over-firing again, the gate false-alarm rate here climbs and the test
fails — at the level that matters to callers.
"""
from __future__ import annotations

import json
from pathlib import Path

import styxx

_CORPUS = Path(__file__).resolve().parents[1] / "benchmarks" / "data" / "benign_text_corpus_v0.jsonl"


def _load():
    return [json.loads(ln) for ln in _CORPUS.read_text().splitlines() if ln.strip()]


def test_benign_corpus_present():
    rows = _load()
    assert len(rows) >= 20
    assert all("prompt" in r and "response" in r for r in rows)


def test_pipeline_false_alarm_rate_is_low():
    """The full reference-less preflight gate must stay quiet on benign text.
    Currently 0/20; the guard allows a small margin (<=10%) so a single
    borderline case doesn't make the suite brittle, while still catching a
    real cross-instrument regression."""
    rows = _load()
    flagged = []
    for r in rows:
        res = styxx.preflight(r["prompt"], r["response"], persist=False)
        if res.needs_revision:
            flagged.append((r.get("category", "?"), r["response"][:60]))
    rate = len(flagged) / len(rows)
    assert rate <= 0.10, (
        f"benign-text gate false-alarm rate {rate:.1%} "
        f"({len(flagged)}/{len(rows)}) — an instrument is over-firing: {flagged}"
    )


def test_ambiguous_content_classes_specifically_pass():
    """The classes that previously false-fired (math/directions/legal/technical
    uses of right/correct/true) must individually pass."""
    rows = {r.get("category"): r for r in _load()}
    for cat in ("math", "directions", "legal", "technical", "anatomy", "physics"):
        r = rows.get(cat)
        if r is None:
            continue
        res = styxx.preflight(r["prompt"], r["response"], persist=False)
        assert not res.needs_revision, f"{cat!r} benign case wrongly flagged: {r['response'][:60]}"
