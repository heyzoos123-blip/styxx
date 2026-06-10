# -*- coding: utf-8 -*-
"""Kill-gate tests for styxx.expguard (B13 experiment-integrity guards).

  K1 — scorer SHA: deterministic, matches an independent hashlib digest,
       changes when the scorer changes, refuses a missing scorer.
  K2 — smoke quarantine (decisive): a smoke run CANNOT produce a citable
       filename, no matter what path the caller asks for; the artifact is
       self-describing (smoke=true, citable=false).
  K3 — instrument floor: a dead instrument cannot emit a live verdict;
       the caller's verdict is overridden and preserved for post-mortem.

Offline, deterministic, stdlib + tmp_path only.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from styxx import expguard
from styxx.expguard import (
    SMOKE_SUFFIX,
    VOID_INSTRUMENT,
    apply_instrument_gate,
    quarantine_path,
    scorer_sha256,
    write_result,
)


@pytest.fixture
def scorer(tmp_path):
    p = tmp_path / "run_experiment_vX.py"
    p.write_text("SCORE = lambda x: 0.5\n", encoding="utf-8")
    return p


# ── K1 — scorer SHA ─────────────────────────────────────────────


def test_K1_sha_deterministic_and_independent(scorer):
    expected = hashlib.sha256(scorer.read_bytes()).hexdigest()
    assert scorer_sha256(scorer) == expected
    assert scorer_sha256(scorer) == scorer_sha256(scorer)


def test_K1_sha_changes_when_scorer_changes(scorer):
    before = scorer_sha256(scorer)
    scorer.write_text("SCORE = lambda x: 0.51\n", encoding="utf-8")
    assert scorer_sha256(scorer) != before


def test_K1_missing_scorer_refused(tmp_path):
    with pytest.raises(FileNotFoundError):
        scorer_sha256(tmp_path / "never_written.py")


def test_K1_result_carries_scorer_sha(tmp_path, scorer):
    out = write_result(
        tmp_path / "result.json", {}, script_path=scorer, smoke=False
    )
    data = json.loads(out.read_text())
    assert data["scorer_sha256"] == scorer_sha256(scorer)


# ── K2 — smoke quarantine ───────────────────────────────────────


def test_K2_smoke_cannot_write_citable_filename(tmp_path, scorer):
    requested = tmp_path / "experiment_result.json"
    out = write_result(requested, {}, script_path=scorer, smoke=True)
    assert out != requested
    assert out.stem.endswith(SMOKE_SUFFIX)
    assert not requested.exists()


def test_K2_smoke_artifact_self_describing(tmp_path, scorer):
    out = write_result(
        tmp_path / "experiment_result.json", {}, script_path=scorer, smoke=True
    )
    data = json.loads(out.read_text())
    assert data["smoke"] is True
    assert data["citable"] is False
    assert "smoke_note" in data


def test_K2_quarantine_idempotent():
    once = quarantine_path("r.json", smoke=True)
    twice = quarantine_path(once, smoke=True)
    assert once == twice


def test_K2_real_run_path_untouched_and_citable(tmp_path, scorer):
    requested = tmp_path / "experiment_result.json"
    out = write_result(requested, {}, script_path=scorer, smoke=False)
    assert out == requested
    data = json.loads(out.read_text())
    assert data["smoke"] is False
    assert data["citable"] is True


# ── K3 — instrument floor ───────────────────────────────────────


def test_K3_dead_instrument_cannot_claim(tmp_path, scorer):
    payload = {"PROGRAM_VERDICT": "ROBUST"}
    out = write_result(
        tmp_path / "r.json",
        payload,
        script_path=scorer,
        smoke=False,
        reference_signal=0.30,
        chance_floor=0.25,  # margin 0.05 < 0.20
    )
    data = json.loads(out.read_text())
    assert data["PROGRAM_VERDICT"] == VOID_INSTRUMENT
    assert data["PROGRAM_VERDICT_voided"] == "ROBUST"


def test_K3_live_instrument_verdict_preserved(tmp_path, scorer):
    payload = {"PROGRAM_VERDICT": "EVADABLE"}
    out = write_result(
        tmp_path / "r.json",
        payload,
        script_path=scorer,
        smoke=False,
        reference_signal=0.80,
        chance_floor=0.35,  # margin 0.45 >= 0.20
    )
    data = json.loads(out.read_text())
    assert data["PROGRAM_VERDICT"] == "EVADABLE"
    assert "PROGRAM_VERDICT_voided" not in data
    assert data["instrument_margin"] == pytest.approx(0.45)


def test_K3_gate_records_floor_and_reference():
    payload: dict = {}
    apply_instrument_gate(
        payload, reference_signal=0.9, chance_floor=0.1
    )
    assert payload["instrument_reference"] == pytest.approx(0.9)
    assert payload["instrument_floor"] == pytest.approx(0.1)
    assert payload["instrument_margin"] == pytest.approx(0.8)
    # margin healthy and no verdict key supplied -> none invented
    assert "PROGRAM_VERDICT" not in payload


def test_K3_boundary_margin_passes():
    payload = {"PROGRAM_VERDICT": "ROBUST"}
    apply_instrument_gate(
        payload, reference_signal=0.55, chance_floor=0.35
    )  # margin exactly 0.20
    assert payload["PROGRAM_VERDICT"] == "ROBUST"
