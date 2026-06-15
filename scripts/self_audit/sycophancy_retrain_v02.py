#!/usr/bin/env python3
"""
sycophancy_retrain_v02.py
=========================

Retrain the sycophancy logistic-regression weights on the CORRECTED
features (word-boundary lexicon matching; "fully"/"compelling" removed).

The v0 coefficients were fit to the old substring-matched features, so
they are stale relative to the precision fixes shipped in 2026-06-15.
This refits on the same 1200-row balanced training corpus
(benchmarks/data/sycophancy/responses_v0.jsonl, 600 sycophantic / 600
calibrated), reports 5-fold stratified CV AUC, and emits drop-in
replacement constants for calibrated_weights_sycophancy_v0.py.

Pure NumPy (no sklearn): standardize features, then L2-regularized
logistic regression by Newton-IRLS (deterministic, ~10 iters).

Acceptance gate (the caller decides whether to ship): the retrain must
hold-or-improve BOTH the CV AUC and the independent attack-seed AUC, and
not raise the seed false-positive rate.

    STYXX_SKIP_SHA=1 python scripts/self_audit/sycophancy_retrain_v02.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from styxx.guardrail.sycophancy_signals import extract_sycophancy_features  # noqa: E402
from styxx.guardrail.calibrated_weights_sycophancy_v0 import (  # noqa: E402
    FEATURE_NAMES, COEFS as OLD_COEFS, INTERCEPT as OLD_INTERCEPT,
    SCALER_MEAN as OLD_MEAN, SCALER_SCALE as OLD_SCALE, MEAN_CV_AUC as OLD_CV_AUC,
)

_RNG = np.random.default_rng(42)
_TRAIN = _REPO_ROOT / "benchmarks" / "data" / "sycophancy" / "responses_v0.jsonl"
_SEEDS = _REPO_ROOT / "styxx" / "attack" / "seeds"
_RLHF = _REPO_ROOT / "data" / "cognometric_rlhf_demo_v0.jsonl"


def _featvec(prompt: str, response: str) -> np.ndarray:
    f = extract_sycophancy_features(prompt or "", response or "")
    return np.array([f[n] for n in FEATURE_NAMES], dtype=float)


def _load_training():
    X, y = [], []
    for ln in _TRAIN.read_text().splitlines():
        if not ln.strip():
            continue
        r = json.loads(ln)
        X.append(_featvec(r.get("question", ""), r["response"]))
        y.append(int(r["label_sycophantic"]))
    return np.array(X), np.array(y)


def _auc(scores: np.ndarray, labels: np.ndarray) -> float:
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    wins = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def _fit_logreg(Xs: np.ndarray, y: np.ndarray, l2: float = 1.0, iters: int = 50):
    """L2-regularized logistic regression via Newton-IRLS on standardized X.
    Returns (weights, intercept). Bias column is not regularized."""
    n, d = Xs.shape
    Xb = np.hstack([np.ones((n, 1)), Xs])  # bias col 0
    w = np.zeros(d + 1)
    reg = np.eye(d + 1) * l2
    reg[0, 0] = 0.0  # don't regularize bias
    for _ in range(iters):
        z = Xb @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
        W = p * (1 - p)
        grad = Xb.T @ (p - y) + reg @ w
        H = Xb.T @ (Xb * W[:, None]) + reg
        try:
            step = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            break
        w -= step
        if np.max(np.abs(step)) < 1e-8:
            break
    return w[1:], w[0]


def _standardize(X):
    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    scale[scale == 0] = 1.0
    return mean, scale


def _predict(X, mean, scale, coefs, intercept):
    Xs = np.clip((X - mean) / scale, -3.0, 3.0)
    z = intercept + Xs @ np.asarray(coefs)
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def _cv_auc(X, y, k=5, l2=1.0):
    idx = _RNG.permutation(len(y))
    folds = np.array_split(idx, k)
    aucs = []
    for i in range(k):
        te = folds[i]
        tr = np.concatenate([folds[j] for j in range(k) if j != i])
        mean, scale = _standardize(X[tr])
        Xtr = np.clip((X[tr] - mean) / scale, -3.0, 3.0)
        w, b = _fit_logreg(Xtr, y[tr], l2=l2)
        scores = _predict(X[te], mean, scale, w, b)
        aucs.append(_auc(scores, y[te]))
    return float(np.mean(aucs)), float(np.std(aucs)), aucs


def _seed_metrics(mean, scale, coefs, intercept):
    pos, neg = [], []
    for ln in (_SEEDS / "sycophancy.jsonl").read_text().splitlines():
        if ln.strip():
            r = json.loads(ln); pos.append(_featvec(r.get("question", ""), r["response"]))
    for ln in (_SEEDS / "sycophancy_fp.jsonl").read_text().splitlines():
        if ln.strip():
            r = json.loads(ln); neg.append(_featvec(r.get("question", ""), r["response"]))
    for ln in _RLHF.read_text().splitlines():
        if ln.strip():
            r = json.loads(ln)
            pos.append(_featvec(r.get("prompt", ""), r["sycophantic"]))
            neg.append(_featvec(r.get("prompt", ""), r["balanced"]))
    pos = np.array(pos); neg = np.array(neg)
    ps = _predict(pos, mean, scale, coefs, intercept)
    ns = _predict(neg, mean, scale, coefs, intercept)
    labels = np.concatenate([np.ones(len(ps)), np.zeros(len(ns))])
    scores = np.concatenate([ps, ns])
    return {
        "auc": round(_auc(scores, labels), 4),
        "fp_at_0.30": round(float((ns > 0.30).mean()), 4),
        "recall_at_0.30": round(float((ps > 0.30).mean()), 4),
    }


def main() -> int:
    X, y = _load_training()
    print(f"training corpus: {len(y)} rows ({int(y.sum())} sycophantic / {int((1-y).sum())} calibrated)")

    cv_mean, cv_std, fold_aucs = _cv_auc(X, y)
    mean, scale = _standardize(X)
    Xs = np.clip((X - mean) / scale, -3.0, 3.0)
    coefs, intercept = _fit_logreg(Xs, y)

    old_seed = _seed_metrics(np.array(OLD_MEAN), np.array(OLD_SCALE), OLD_COEFS, OLD_INTERCEPT)
    new_seed = _seed_metrics(mean, scale, coefs, intercept)

    print(f"\n            {'OLD (v0)':>12} {'NEW (v0.2)':>12}")
    print(f"CV AUC      {OLD_CV_AUC:>12.4f} {cv_mean:>12.4f}  (±{cv_std:.4f})")
    print(f"seed AUC    {old_seed['auc']:>12} {new_seed['auc']:>12}")
    print(f"seed FP@.30 {old_seed['fp_at_0.30']:>12} {new_seed['fp_at_0.30']:>12}")
    print(f"seed recall {old_seed['recall_at_0.30']:>12} {new_seed['recall_at_0.30']:>12}")

    ship = bool(cv_mean >= OLD_CV_AUC - 0.005 and new_seed["auc"] >= old_seed["auc"]
                and new_seed["fp_at_0.30"] <= old_seed["fp_at_0.30"])
    print(f"\nACCEPTANCE GATE: {'PASS — retrain is better/equal' if ship else 'FAIL — keep v0 weights'}")

    out = {
        "cv_mean_auc": round(cv_mean, 4), "cv_std_auc": round(cv_std, 4),
        "fold_aucs": [round(a, 4) for a in fold_aucs],
        "old_seed": old_seed, "new_seed": new_seed,
        "ship": ship,
        "weights": {
            "INTERCEPT": round(float(intercept), 6),
            "COEFS": [round(float(c), 6) for c in coefs],
            "SCALER_MEAN": [round(float(m), 6) for m in mean],
            "SCALER_SCALE": [round(float(s), 6) for s in scale],
        },
    }
    out_dir = _REPO_ROOT / "papers" / "agent-self-audit" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sycophancy_retrain_v02.json").write_text(json.dumps(out, indent=2))
    print(f"wrote {out_dir / 'sycophancy_retrain_v02.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
