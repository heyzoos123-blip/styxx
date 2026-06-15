# -*- coding: utf-8 -*-
"""Reference-grounded overconfidence (2026-06-15).

Text-only overconfidence is a construct ceiling: it scores the confidence
REGISTER and fires equally on confident-correct and confident-wrong text
(calibration AUC ~0.52 — chance). When a correct_reference is supplied and
deception is NLI/emb-grounded, P(contradiction) is the wrongness signal, so
``register × wrongness`` becomes a discriminative miscalibration score
(mechanism AUC 0.52 → 1.00, see
scripts/self_audit/overconfidence_grounding_eval.py). Grounded overconfidence
then re-enters the gate, mirroring how grounded deception re-enters the
composite.

The live contradiction signal needs the NLI backend (deception_v2), so the
grounded *integration* path is exercised here by simulating a grounded score
dict. The combiner and the grounded gate logic are tested deterministically.
"""
from __future__ import annotations

import styxx.mcp.server as server
from styxx.mcp.server import (
    COGN_COMPOSITE_KEYS,
    COGN_COMPOSITE_KEYS_WITH_REFERENCE,
    _grounded_overconfidence,
    _gate_excluded,
    _gate_keys,
    _needs_revision,
    tool_cogn_audit,
)


# ── the combiner: register × wrongness ──

def test_grounded_overconfidence_truth_table():
    # confident + wrong  → high
    assert _grounded_overconfidence(0.95, 0.95) > 0.85
    # confident + correct → ~0 (no contradiction)
    assert _grounded_overconfidence(0.95, 0.0) == 0.0
    # hedged + wrong → low (no confidence register)
    assert _grounded_overconfidence(0.05, 0.95) < 0.10
    # clamped to [0, 1]
    assert _grounded_overconfidence(2.0, 2.0) == 1.0
    assert _grounded_overconfidence(-1.0, 0.9) == 0.0


# ── gate eligibility flips with grounding ──

def test_overconfidence_gate_excluded_only_when_text_only():
    # text-only: overconfidence is excluded from the gate (construct ceiling)
    assert "overconfidence" in _gate_excluded(grounded=False)
    assert "overconfidence" not in _gate_keys(COGN_COMPOSITE_KEYS, grounded=False)
    # grounded: overconfidence is discriminative and re-enters the gate
    assert _gate_excluded(grounded=True) == set()
    assert "overconfidence" in _gate_keys(COGN_COMPOSITE_KEYS_WITH_REFERENCE, grounded=True)


def test_grounded_overconfidence_can_trip_the_gate():
    # A confident, contradicted (wrong) claim: grounded overconfidence high.
    scores = {"sycophancy": 0.05, "deception": 0.95, "overconfidence": 0.90}
    assert _needs_revision(scores, COGN_COMPOSITE_KEYS_WITH_REFERENCE, grounded=True) is True


def test_grounded_overconfidence_does_not_punish_confident_correct():
    # Confident but CORRECT: contradiction ~0 → grounded overconfidence ~0,
    # deception ~0; nothing discriminative fires → passes.
    scores = {"sycophancy": 0.05, "deception": 0.02, "overconfidence": 0.0}
    assert _needs_revision(scores, COGN_COMPOSITE_KEYS_WITH_REFERENCE, grounded=True) is False


# ── integration: tool_cogn_audit grounded path (simulated backend) ──

def _patch_grounded(monkeypatch, register, contradiction):
    """Force _cogn_score_all_meta to report a grounded (nli) audit with the
    given text-only register and contradiction (deception) score."""
    def fake(prompt, response, correct_reference=None):
        return ({"sycophancy": 0.05, "deception": float(contradiction),
                 "overconfidence": float(register), "refusal": 0.0}, "nli")
    monkeypatch.setattr(server, "_cogn_score_all_meta", fake)


def test_tool_cogn_audit_grounds_overconfidence_for_confident_lie(monkeypatch):
    _patch_grounded(monkeypatch, register=0.95, contradiction=0.95)
    out = tool_cogn_audit({"prompt": "when did the titanic sink?",
                           "response": "definitely 1911",
                           "correct_reference": "1912"})
    assert out["overconfidence_grounded"] is True
    # overconfidence is replaced by register × wrongness
    assert abs(out["scores"]["overconfidence"] - 0.95 * 0.95) < 1e-6
    # and it is gate-eligible now
    assert "overconfidence" in out["gate_keys"]
    assert out["needs_revision"] is True


def test_tool_cogn_audit_grounded_overconfidence_clears_confident_truth(monkeypatch):
    _patch_grounded(monkeypatch, register=0.95, contradiction=0.0)
    out = tool_cogn_audit({"prompt": "when did the titanic sink?",
                           "response": "definitely 1912",
                           "correct_reference": "1912"})
    assert out["overconfidence_grounded"] is True
    # confident + correct → grounded overconfidence collapses to 0
    assert out["scores"]["overconfidence"] == 0.0
    assert out["needs_revision"] is False


def test_text_only_path_unchanged(monkeypatch):
    """Without grounding (the default, backend-less behavior), overconfidence
    stays text-only and gate-excluded — no regression."""
    out = tool_cogn_audit({"prompt": "what is 2+2?", "response": "the answer is 4"})
    assert out["overconfidence_grounded"] is False
    assert "overconfidence" not in out["gate_keys"]
    assert out["needs_revision"] is False
