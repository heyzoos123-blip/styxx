# -*- coding: utf-8 -*-
"""styxx.relock — the verifier-side re-locking harness (B11).

The robustness arc (adversarial-curve v1→v4) established that a probe
FROZEN at calibration time can be defeated, while audit-time RE-FIT
recovers the read — but a naive refit_max over all layers is
multiple-comparisons-inflated: under pure noise, the max over 28 layers
of per-layer CV accuracy sits well above chance. A verifier that selects
its probe that way will certify noise.

This module is the deployment-faithful selection procedure the
STYXX_PROTOCOL re-locking section specifies. Given a VERIFIER-PRIVATE
calibration set of residual activations spanning the three populations
(``prime`` — content genuinely present; ``abort`` — content genuinely
absent; ``lie`` — the audited read), it:

  1. fits a per-layer linear probe on a PROBE_FIT split of the ``lie``
     population and scores it on a DISJOINT PROBE_TEST split (READ_B,
     the deployment-faithful read — never same-items CV);
  2. applies the **permutation-corrected selection penalty**:
     ``corrected[li] = acc[li] − p95(label-permutation null at li)``;
     the layer is selected on the corrected statistic, which
     concentrates at 0 under noise — the max-inflation is paid for
     inside the statistic, not excused in prose;
  3. enforces the PRIME / ABORT validity gates from STYXX_PROTOCOL §4 on
     the selected probe (UNINFORMATIVE if it cannot read a present
     state; VOID if it elevates on an absent one);
  4. emits a ``RelockCertificate`` carrying the calibration-set SHA-256,
     the selected layer, the permutation floor, the PRIME/ABORT reads,
     and the re-locked probe-weight SHA-256 — every number a third
     party needs to re-derive the selection;
  5. at deployment, ``read()`` returns ``state="ABSTAIN"`` when the
     input's activation is off-manifold relative to the calibration
     distribution at the selected layer — silent failure becomes honest
     abstention.

Honest boundary: this is the SELECTION AND GATING apparatus, validated
here on synthetic activations only. It does not make a weak probe
strong, does not reach closed models (no activations, no certificate),
and all thresholds are per-(model, substrate) and MUST be recalibrated
before any cross-substrate use (STYXX_PROTOCOL §4). numpy only; no
sklearn, no LLM.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = [
    "RelockCertificate",
    "RelockResult",
    "relock",
    "read",
]

# Default gate thresholds. Per STYXX_PROTOCOL §4 these are
# per-(model, substrate) quantities; the defaults exist so the synthetic
# harness is runnable, not so deployments can skip recalibration.
DEFAULT_MIN_CORRECTED = 0.05   # corrected elevation below this -> UNINFORMATIVE
DEFAULT_PRIME_MIN = 0.20       # prime read must beat chance by this -> else UNINFORMATIVE
DEFAULT_ABORT_TOL = 0.10       # abort read above chance+tol -> VOID (fabrication)
DEFAULT_ABSTAIN_Q = 0.99       # calibration self-distance quantile for ABSTAIN
DEFAULT_N_PERM = 200
DEFAULT_FIT_FRACTION = 0.6


# ── deterministic numpy logistic probe ──────────────────────────


def _fit_logistic(
    X: np.ndarray, y: np.ndarray, *, l2: float = 1e-2, iters: int = 300, lr: float = 0.5
) -> Tuple[np.ndarray, float]:
    """Full-batch gradient-descent logistic regression. Deterministic."""
    n, d = X.shape
    w = np.zeros(d, dtype=np.float64)
    b = 0.0
    for _ in range(iters):
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))
        g = p - y
        w -= lr * (X.T @ g / n + l2 * w)
        b -= lr * float(g.mean())
    return w, b


def _accuracy(w: np.ndarray, b: float, X: np.ndarray, y: np.ndarray) -> float:
    pred = (X @ w + b) > 0.0
    return float((pred == (y > 0.5)).mean())


def _standardize(
    X: np.ndarray, mu: Optional[np.ndarray] = None, sd: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if mu is None:
        mu = X.mean(axis=0)
        sd = X.std(axis=0) + 1e-8
    return (X - mu) / sd, mu, sd


def _sha256_arrays(*arrays: np.ndarray) -> str:
    """Content hash over dtype/shape/bytes of each array, order-sensitive."""
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(a)
        h.update(str(a.dtype).encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()


def _chance(y: np.ndarray) -> float:
    """Majority-class rate — the no-information accuracy for this label set."""
    m = float(y.mean())
    return max(m, 1.0 - m)


# ── certificate ─────────────────────────────────────────────────


@dataclass
class RelockCertificate:
    """Everything a third party needs to re-derive the probe selection."""

    state: str                      # HELD-READY | UNINFORMATIVE | VOID | ERROR
    selected_layer: Optional[int]
    corrected_elevation: float      # acc[sel] − p95(perm null at sel); the selection statistic
    read_b_accuracy: float          # deployment-faithful accuracy at the selected layer
    floor_perm_p95: float           # p95 of the max-over-layers permutation null (the evasion target)
    prime_read: float
    prime_chance: float
    abort_read: float
    abort_chance: float
    calibration_sha256: str
    probe_sha256: Optional[str]
    n_layers: int
    n_permutations: int
    seed: int
    thresholds: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RelockResult:
    """Certificate + the private state needed to run deployment reads."""

    certificate: RelockCertificate
    probe_weights: Optional[np.ndarray]
    probe_bias: float
    feature_mu: Optional[np.ndarray]
    feature_sd: Optional[np.ndarray]
    abstain_threshold: float        # calibration self-distance quantile at selected layer
    calib_layer_mu: Optional[np.ndarray]
    calib_layer_sd: Optional[np.ndarray]


# ── the re-lock procedure ───────────────────────────────────────


def relock(
    activations: np.ndarray,
    labels: np.ndarray,
    populations: np.ndarray,
    *,
    n_permutations: int = DEFAULT_N_PERM,
    fit_fraction: float = DEFAULT_FIT_FRACTION,
    min_corrected: float = DEFAULT_MIN_CORRECTED,
    prime_min: float = DEFAULT_PRIME_MIN,
    abort_tol: float = DEFAULT_ABORT_TOL,
    abstain_quantile: float = DEFAULT_ABSTAIN_Q,
    seed: int = 0,
) -> RelockResult:
    """Run verifier-side probe re-locking on a private calibration set.

    activations : (n_items, n_layers, d) float array of residuals
    labels      : (n_items,) binary {0,1} gold-class labels
    populations : (n_items,) strings in {'prime', 'abort', 'lie'}

    Returns a RelockResult whose certificate state follows STYXX_PROTOCOL
    precedence (ERROR > VOID > UNINFORMATIVE > HELD-READY). ABSTAIN is a
    deployment-read state, emitted by read(), not by relock().
    """
    thresholds = {
        "min_corrected": min_corrected,
        "prime_min": prime_min,
        "abort_tol": abort_tol,
        "abstain_quantile": abstain_quantile,
    }

    def _error(note: str) -> RelockResult:
        cert = RelockCertificate(
            state="ERROR", selected_layer=None, corrected_elevation=0.0,
            read_b_accuracy=0.0, floor_perm_p95=0.0,
            prime_read=0.0, prime_chance=0.0, abort_read=0.0, abort_chance=0.0,
            calibration_sha256="", probe_sha256=None,
            n_layers=0, n_permutations=n_permutations, seed=seed,
            thresholds=thresholds, notes=[note],
        )
        return RelockResult(cert, None, 0.0, None, None, float("inf"), None, None)

    activations = np.asarray(activations, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.float64).ravel()
    populations = np.asarray(populations).ravel()

    if activations.ndim != 3:
        return _error("activations must be (n_items, n_layers, d)")
    n_items, n_layers, d = activations.shape
    if not (len(labels) == len(populations) == n_items):
        return _error("labels/populations length mismatch with activations")
    for pop in ("prime", "abort", "lie"):
        if int((populations == pop).sum()) < 4:
            return _error(f"calibration set must span all three populations; '{pop}' < 4 items")
    if set(np.unique(labels)) - {0.0, 1.0}:
        return _error("labels must be binary {0,1}")

    calibration_sha = _sha256_arrays(activations, labels, populations.astype("U16"))
    rng = np.random.default_rng(seed)

    lie_idx = np.flatnonzero(populations == "lie")
    prime_idx = np.flatnonzero(populations == "prime")
    abort_idx = np.flatnonzero(populations == "abort")

    # Deployment-faithful split: probe fit on PROBE_FIT, scored on a
    # DISJOINT PROBE_TEST (READ_B). Same-items CV is an existence read
    # only and never gates anything here.
    perm = rng.permutation(len(lie_idx))
    n_fit = max(2, int(round(fit_fraction * len(lie_idx))))
    fit_idx, test_idx = lie_idx[perm[:n_fit]], lie_idx[perm[n_fit:]]
    if len(test_idx) < 2 or len(np.unique(labels[fit_idx])) < 2:
        return _error("lie population too small or single-class after split")

    # Per-layer real accuracy + label-permutation null (refit per
    # permutation — the null must contain the fit-and-select process,
    # otherwise the penalty is cosmetic).
    acc = np.zeros(n_layers)
    null = np.zeros((n_layers, n_permutations))
    fits: List[Tuple[np.ndarray, float, np.ndarray, np.ndarray]] = []
    for li in range(n_layers):
        Xf, mu, sd = _standardize(activations[fit_idx, li, :])
        Xt = (activations[test_idx, li, :] - mu) / sd
        w, b = _fit_logistic(Xf, labels[fit_idx])
        acc[li] = _accuracy(w, b, Xt, labels[test_idx])
        fits.append((w, b, mu, sd))
        all_idx = np.concatenate([fit_idx, test_idx])
        y_all = labels[all_idx].copy()
        for bi in range(n_permutations):
            y_perm = rng.permutation(y_all)
            yf, yt = y_perm[: len(fit_idx)], y_perm[len(fit_idx):]
            if len(np.unique(yf)) < 2:
                null[li, bi] = _chance(yt)
                continue
            wp, bp = _fit_logistic(Xf, yf)
            null[li, bi] = _accuracy(wp, bp, Xt, yt)

    corrected = acc - np.percentile(null, 95, axis=1)
    sel = int(np.argmax(corrected))
    corrected_elev = float(corrected[sel])
    # Global floor: the null distribution of the SELECTED (max-over-layers)
    # statistic — the number an evader has to hide below.
    floor = float(np.percentile(null.max(axis=0), 95))

    w, b, mu, sd = fits[sel]

    # PRIME / ABORT gates on the selected, re-locked probe.
    Xp = (activations[prime_idx, sel, :] - mu) / sd
    Xa = (activations[abort_idx, sel, :] - mu) / sd
    prime_read = _accuracy(w, b, Xp, labels[prime_idx])
    abort_read = _accuracy(w, b, Xa, labels[abort_idx])
    prime_chance = _chance(labels[prime_idx])
    abort_chance = _chance(labels[abort_idx])

    notes: List[str] = []
    if abort_read > abort_chance + abort_tol:
        state = "VOID"
        notes.append(
            f"ABORT gate fired: read {abort_read:.3f} elevates above chance "
            f"{abort_chance:.3f}+{abort_tol} on content-absent items — channel fabricates."
        )
    elif corrected_elev < min_corrected or prime_read < prime_chance + prime_min:
        state = "UNINFORMATIVE"
        if corrected_elev < min_corrected:
            notes.append(
                f"corrected elevation {corrected_elev:.3f} < {min_corrected} — "
                "no layer survives the selection penalty."
            )
        if prime_read < prime_chance + prime_min:
            notes.append(
                f"PRIME gate failed: read {prime_read:.3f} vs chance {prime_chance:.3f} — "
                "channel never shown to read a present state."
            )
    else:
        state = "HELD-READY"

    probe_sha = _sha256_arrays(
        np.round(w, 12), np.asarray([b]), np.asarray([sel], dtype=np.int64)
    )

    # ABSTAIN manifold: z-distance of calibration items to the calibration
    # distribution at the selected layer; deployment inputs beyond the
    # abstain_quantile of these self-distances are off-manifold.
    layer_acts = activations[:, sel, :]
    lmu = layer_acts.mean(axis=0)
    lsd = layer_acts.std(axis=0) + 1e-8
    self_dist = np.sqrt((((layer_acts - lmu) / lsd) ** 2).mean(axis=1))
    abstain_thr = float(np.quantile(self_dist, abstain_quantile))

    cert = RelockCertificate(
        state=state,
        selected_layer=sel,
        corrected_elevation=corrected_elev,
        read_b_accuracy=float(acc[sel]),
        floor_perm_p95=floor,
        prime_read=float(prime_read),
        prime_chance=prime_chance,
        abort_read=float(abort_read),
        abort_chance=abort_chance,
        calibration_sha256=calibration_sha,
        probe_sha256=probe_sha,
        n_layers=n_layers,
        n_permutations=n_permutations,
        seed=seed,
        thresholds=thresholds,
        notes=notes,
    )
    return RelockResult(
        certificate=cert,
        probe_weights=w,
        probe_bias=b,
        feature_mu=mu,
        feature_sd=sd,
        abstain_threshold=abstain_thr,
        calib_layer_mu=lmu,
        calib_layer_sd=lsd,
    )


# ── deployment read ─────────────────────────────────────────────


def read(result: RelockResult, activation: np.ndarray) -> Dict[str, Any]:
    """Read one deployment input through the re-locked probe.

    activation : (n_layers, d) residuals for the input being audited.

    Returns a dict with ``state`` ∈ {ABSTAIN, READ, REFUSED}. REFUSED
    when the certificate is not HELD-READY (an inadmissible probe must
    not produce reads). ABSTAIN when the input is off-manifold relative
    to the calibration distribution at the selected layer.
    """
    cert = result.certificate
    if cert.state != "HELD-READY":
        return {
            "state": "REFUSED",
            "reason": f"certificate state is {cert.state}; reads are inadmissible",
            "probe_sha256": cert.probe_sha256,
        }
    activation = np.asarray(activation, dtype=np.float64)
    x = activation[cert.selected_layer]
    z = (x - result.calib_layer_mu) / result.calib_layer_sd
    dist = float(np.sqrt((z ** 2).mean()))
    if dist > result.abstain_threshold:
        return {
            "state": "ABSTAIN",
            "off_manifold_distance": dist,
            "abstain_threshold": result.abstain_threshold,
            "reason": "input is off-manifold vs the verifier's calibration set; "
                      "a read here would be a silent failure.",
            "probe_sha256": cert.probe_sha256,
        }
    xs = (x - result.feature_mu) / result.feature_sd
    score = float(xs @ result.probe_weights + result.probe_bias)
    return {
        "state": "READ",
        "predicted_class": int(score > 0.0),
        "score": score,
        "off_manifold_distance": dist,
        "probe_sha256": cert.probe_sha256,
        "calibration_sha256": cert.calibration_sha256,
    }


# ── runnable harness (synthetic; methodology demo, not evidence) ─


def _synthetic_calibration(
    seed: int, *, n_per_pop: int = 60, n_layers: int = 6, d: int = 8, signal_layer: int = 3,
    signal: float = 1.5,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Synthetic activations: class-separable at signal_layer in 'lie' and
    'prime' items, pure noise in 'abort' items (content absent)."""
    rng = np.random.default_rng(seed)
    pops = np.array(["lie"] * n_per_pop + ["prime"] * n_per_pop + ["abort"] * n_per_pop)
    y = rng.integers(0, 2, size=3 * n_per_pop).astype(float)
    X = rng.normal(size=(3 * n_per_pop, n_layers, d))
    present = np.flatnonzero(pops != "abort")
    X[present, signal_layer, 0] += signal * (2 * y[present] - 1)
    return X, y, pops


def main(argv: Optional[List[str]] = None) -> int:
    """Run the re-lock harness end-to-end on synthetic data and write the
    certificate through styxx.expguard (B13 guards apply)."""
    import argparse
    from pathlib import Path

    from . import expguard

    ap = argparse.ArgumentParser(prog="python -m styxx.relock")
    ap.add_argument("--out", default="relock_demo_result.json")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-permutations", type=int, default=DEFAULT_N_PERM)
    args = ap.parse_args(argv)

    X, y, pops = _synthetic_calibration(args.seed)
    res = relock(X, y, pops, n_permutations=(20 if args.smoke else args.n_permutations),
                 seed=args.seed)
    payload: Dict[str, Any] = {
        "experiment": "relock harness (SYNTHETIC methodology demo — not evidence)",
        "certificate": res.certificate.to_dict(),
    }
    out = expguard.write_result(
        Path(args.out), payload, script_path=Path(__file__), smoke=args.smoke,
        reference_signal=res.certificate.read_b_accuracy,
        chance_floor=res.certificate.floor_perm_p95,
    )
    print(json.dumps({"written": str(out), "state": res.certificate.state}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
