# -*- coding: utf-8 -*-
"""Kill-gate tests for styxx.relock (B11 re-locking harness).

  K1 — determinism: same calibration + seed -> identical certificate,
       identical calibration/probe hashes.
  K2 — the selection penalty (decisive): on PURE-NOISE calibration the
       corrected statistic concentrates at ~0 and the certificate is
       UNINFORMATIVE — a naive argmax-over-layers read on the same data
       is visibly inflated above chance, which is exactly the failure
       the penalty exists to kill. With a real signal layer, that layer
       is selected and the certificate is HELD-READY.
  K3 — validity gates: a channel that elevates on content-absent items
       is VOID (fabrication); reads through a non-HELD-READY
       certificate are REFUSED.
  K4 — ABSTAIN: an off-manifold deployment input gets ABSTAIN, an
       on-manifold one gets READ.
  K5 — input contract: malformed calibration -> state ERROR, never an
       exception, never a read.

Synthetic activations only; offline; deterministic.
"""
from __future__ import annotations

import numpy as np
import pytest

from styxx.relock import (
    _synthetic_calibration,
    read,
    relock,
)

N_PERM = 60  # small but real; keeps the suite fast


@pytest.fixture(scope="module")
def signal_result():
    X, y, pops = _synthetic_calibration(seed=7)
    return relock(X, y, pops, n_permutations=N_PERM, seed=7)


# ── K1 — determinism ────────────────────────────────────────────


def test_K1_same_inputs_same_certificate(signal_result):
    X, y, pops = _synthetic_calibration(seed=7)
    again = relock(X, y, pops, n_permutations=N_PERM, seed=7)
    a, b = signal_result.certificate, again.certificate
    assert a.to_dict() == b.to_dict()
    assert a.calibration_sha256 == b.calibration_sha256
    assert a.probe_sha256 == b.probe_sha256


def test_K1_calibration_hash_tracks_data():
    X, y, pops = _synthetic_calibration(seed=7)
    h1 = relock(X, y, pops, n_permutations=8, seed=7).certificate.calibration_sha256
    X2 = X.copy()
    X2[0, 0, 0] += 1e-6
    h2 = relock(X2, y, pops, n_permutations=8, seed=7).certificate.calibration_sha256
    assert h1 != h2


# ── K2 — the selection penalty ──────────────────────────────────


def test_K2_pure_noise_is_uninformative_not_inflated():
    X, y, pops = _synthetic_calibration(seed=11, signal=0.0)  # no signal anywhere
    res = relock(X, y, pops, n_permutations=N_PERM, seed=11)
    cert = res.certificate
    assert cert.state == "UNINFORMATIVE"
    # The naive (uncorrected) max-over-layers read sits above the floor —
    # the inflation is real on this very dataset...
    assert cert.read_b_accuracy >= 0.5
    # ...but the corrected statistic concentrates at ~0: the penalty
    # paid for the max inside the statistic.
    assert cert.corrected_elevation < 0.05


def test_K2_signal_layer_selected_and_held_ready(signal_result):
    cert = signal_result.certificate
    assert cert.state == "HELD-READY"
    assert cert.selected_layer == 3  # the synthetic signal layer
    assert cert.corrected_elevation >= 0.05
    assert cert.read_b_accuracy > cert.floor_perm_p95


# ── K3 — validity gates ─────────────────────────────────────────


def test_K3_fabricating_channel_is_void():
    # Plant the SAME class signal in the 'abort' (content-absent)
    # population: the probe now elevates where content is absent ->
    # fabrication -> VOID, regardless of how well it reads 'lie' items.
    X, y, pops = _synthetic_calibration(seed=13)
    abort = np.flatnonzero(pops == "abort")
    X[abort, 3, 0] += 1.5 * (2 * y[abort] - 1)
    res = relock(X, y, pops, n_permutations=N_PERM, seed=13)
    assert res.certificate.state == "VOID"
    assert any("ABORT" in n for n in res.certificate.notes)


def test_K3_reads_through_invalid_certificate_refused():
    X, y, pops = _synthetic_calibration(seed=11, signal=0.0)
    res = relock(X, y, pops, n_permutations=N_PERM, seed=11)
    assert res.certificate.state != "HELD-READY"
    out = read(res, X[0])
    assert out["state"] == "REFUSED"
    assert "predicted_class" not in out


# ── K4 — ABSTAIN on off-manifold inputs ─────────────────────────


def test_K4_off_manifold_input_abstains(signal_result):
    X, _, _ = _synthetic_calibration(seed=7)
    weird = X[0].copy()
    weird[signal_result.certificate.selected_layer] += 25.0  # far off-manifold
    out = read(signal_result, weird)
    assert out["state"] == "ABSTAIN"
    assert out["off_manifold_distance"] > out["abstain_threshold"]


def test_K4_on_manifold_input_reads(signal_result):
    X, y, _ = _synthetic_calibration(seed=7)
    out = read(signal_result, X[5])
    assert out["state"] == "READ"
    assert out["predicted_class"] in (0, 1)
    assert out["calibration_sha256"] == signal_result.certificate.calibration_sha256


def test_K4_probe_actually_reads_signal(signal_result):
    # On-manifold items with planted signal: the re-locked probe should
    # recover the class well above chance across the lie population.
    X, y, pops = _synthetic_calibration(seed=7)
    lie = np.flatnonzero(pops == "lie")
    outs = [read(signal_result, X[i]) for i in lie]
    readable = [(o, y[i]) for o, i in zip(outs, lie) if o["state"] == "READ"]
    assert len(readable) >= len(lie) * 0.9
    acc = np.mean([o["predicted_class"] == yy for o, yy in readable])
    assert acc > 0.8


# ── K5 — input contract ─────────────────────────────────────────


def test_K5_missing_population_is_error():
    X, y, pops = _synthetic_calibration(seed=3)
    pops = np.where(pops == "abort", "lie", pops)  # no abort items at all
    res = relock(X, y, pops, n_permutations=8, seed=3)
    assert res.certificate.state == "ERROR"
    assert read(res, X[0])["state"] == "REFUSED"


def test_K5_bad_shapes_are_error():
    res = relock(np.zeros((4, 4)), np.zeros(4), np.array(["lie"] * 4),
                 n_permutations=8)
    assert res.certificate.state == "ERROR"


def test_K5_nonbinary_labels_are_error():
    X, y, pops = _synthetic_calibration(seed=3)
    y = y + 0.5
    res = relock(X, y, pops, n_permutations=8, seed=3)
    assert res.certificate.state == "ERROR"
