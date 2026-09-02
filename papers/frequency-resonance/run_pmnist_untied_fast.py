# -*- coding: utf-8 -*-
"""
run_pmnist_untied_fast.py -- PLUMBING for the frozen PREREG_pmnist_untied_2026_09_02 runner.

The preregistration's runner is run_pmnist_untied.py (which imports run_pmnist_ablation). This
file changes NO arm, NO model, NO seed, NO step count and NO gate. It does two things a 4-core CPU
needs and a GPU does not:

  1. swaps the doubling scan (run_pmnist_ablation.lin_scan) for an exact chunked scan in real
     arithmetic that computes the same recurrence h_t = lam h_{t-1} + u_t for time-invariant lam
     (every core in this arc builds lam that way); the swap is red-teamed against seq_scan --
     forward, and gradients into theta and nu -- before any training, and the deviations are
     written into the result;
  2. runs each (arm, seed) job in its own process (`--job ARM SEED`), then `--merge` assembles
     exactly the result dict run_pmnist_untied.main builds and scores it with the same
     Experiment. RNG is per-job in the frozen runner too (train reseeds on entry), so the sharded
     run draws the same batches as the sequential one.

If any of this moves the numbers, PREREG gate G_P_anchors (FREE and CLAMPED within 0.03 of the
committed GPU receipt) is the detector, and the verdict is INVALID__plumbing_anchors_drifted.

  python run_pmnist_untied_fast.py --redteam
  python run_pmnist_untied_fast.py --job free 0        # one of six
  python run_pmnist_untied_fast.py --merge
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_argv = sys.argv[:]
sys.argv = [sys.argv[0]]                       # the frozen modules read --smoke from argv; never here
import run_pmnist_ablation as R                # noqa: E402
import run_pmnist_untied as U                  # noqa: E402
from styxx.protocol import Experiment          # noqa: E402

sys.argv = _argv
CHUNK = 28
JOBS = [(arm, s) for arm in ("free", "clamped", "real2") for s in R.SEEDS]
JOB_FILE = "pmnist_untied_job_{arm}_{seed}.json"
_REFERENCE_SCAN = R.lin_scan


def chunk_scan(A, X):
    """h_t = A_t h_{t-1} + X_t, exactly, for A constant along T; real arithmetic, chunks of CHUNK.
    Falls back to the frozen module's scan when A varies in time or T is not a multiple."""
    B, T, D = X.shape
    C = CHUNK
    if T % C or not torch.equal(A[:, 1:], A[:, :1].expand(B, T - 1, D)):
        return _REFERENCE_SCAN(A, X)
    NC = T // C
    lam = A[:, 0]
    is_c = X.is_complex()
    if is_c:
        lr, li, xr, xi = lam.real, lam.imag, X.real, X.imag
    else:
        lr, li, xr, xi = lam, torch.zeros_like(lam), X, torch.zeros_like(X)
    pr, pi = [torch.ones_like(lr)], [torch.zeros_like(li)]
    for _ in range(C):
        a, b = pr[-1], pi[-1]
        pr.append(a * lr - b * li)
        pi.append(a * li + b * lr)
    Pr, Pi = torch.stack(pr, 1), torch.stack(pi, 1)                    # (B, C+1, D): lam^k
    idx = torch.arange(C).view(C, 1) - torch.arange(C).view(1, C)       # j - i
    mask = (idx >= 0).view(1, C, C, 1).to(xr.dtype)
    idx = idx.clamp(min=0)
    Tr, Ti = Pr[:, idx, :] * mask, Pi[:, idx, :] * mask                 # (B, C, C, D) Toeplitz of powers
    xr_c, xi_c = xr.reshape(B, NC, C, D), xi.reshape(B, NC, C, D)
    yr = torch.einsum("bjid,bcid->bcjd", Tr, xr_c) - torch.einsum("bjid,bcid->bcjd", Ti, xi_c)
    yi = torch.einsum("bjid,bcid->bcjd", Tr, xi_c) + torch.einsum("bjid,bcid->bcjd", Ti, xr_c)
    LCr, LCi = Pr[:, C], Pi[:, C]                                       # lam^C
    hr, hi = torch.zeros_like(lr), torch.zeros_like(li)
    cr, ci = [], []
    for c in range(NC):
        cr.append(hr)
        ci.append(hi)
        hr, hi = (LCr * hr - LCi * hi + yr[:, c, -1], LCr * hi + LCi * hr + yi[:, c, -1])
    Cr, Ci = torch.stack(cr, 1), torch.stack(ci, 1)                     # (B, NC, D): carry into chunk
    Qr, Qi = Pr[:, 1:C + 1], Pi[:, 1:C + 1]                             # lam^{j+1}
    outr = yr + (Qr.unsqueeze(1) * Cr.unsqueeze(2) - Qi.unsqueeze(1) * Ci.unsqueeze(2))
    outi = yi + (Qr.unsqueeze(1) * Ci.unsqueeze(2) + Qi.unsqueeze(1) * Cr.unsqueeze(2))
    outr, outi = outr.reshape(B, T, D), outi.reshape(B, T, D)
    return torch.complex(outr, outi) if is_c else outr


def redteam() -> dict:
    """The swap is equal to seq_scan or the run does not start."""
    torch.manual_seed(0)
    B, T, D = 4, R.T_LEN, 16
    mag = torch.rand(B, D) * 0.5 + 0.5
    th = torch.rand(B, D) * math.pi
    lam = torch.polar(mag, th).view(B, 1, D).expand(B, T, D)
    X = torch.randn(B, T, D, dtype=torch.cfloat, requires_grad=True)
    X2 = X.detach().clone().requires_grad_(True)
    ref, new = R.seq_scan(lam, X), chunk_scan(lam, X2)
    d_fwd = (ref - new).abs().max().item()
    (ref.abs() ** 2).sum().backward()
    (new.abs() ** 2).sum().backward()
    d_grad = (X.grad - X2.grad).abs().max().item() / X.grad.abs().max().item()
    lamr = (torch.rand(B, D) * 0.5 + 0.5).view(B, 1, D).expand(B, T, D)
    Xr = torch.randn(B, T, D)
    d_real = (R.seq_scan(lamr, Xr) - chunk_scan(lamr, Xr)).abs().max().item()
    torch.manual_seed(1)
    m1 = R.CLRU(16, 8, True)
    torch.manual_seed(1)
    m2 = R.CLRU(16, 8, True)
    x = torch.randn(2, R.T_LEN, 8)
    R.lin_scan = _REFERENCE_SCAN
    m1(x).pow(2).sum().backward()
    R.lin_scan = chunk_scan
    m2(x).pow(2).sum().backward()
    d_theta = (m1.theta.grad - m2.theta.grad).abs().max().item() / m1.theta.grad.abs().max().item()
    d_nu = (m1.nu.grad - m2.nu.grad).abs().max().item() / m1.nu.grad.abs().max().item()
    out = {"scan": "chunked exact scan, real arithmetic, chunk=%d, time-invariant lam" % CHUNK,
           "vs_seq_scan_fwd_max_abs": d_fwd, "vs_seq_scan_grad_max_rel": d_grad,
           "real_path_vs_seq_scan_max_abs": d_real,
           "clru_dtheta_max_rel": d_theta, "clru_dnu_max_rel": d_nu, "tolerance": 1e-4}
    for k, v in out.items():
        if isinstance(v, float) and k != "tolerance":
            assert v < 1e-4, (k, v)
    print("  [redteam-fast] " + json.dumps(out), flush=True)
    return out


def install():
    R.lin_scan = chunk_scan      # CLRU calls the module global; RealBank calls R.lin_scan


def run_job(arm: str, seed: int) -> Path:
    rt = redteam()
    install()
    R.redteam()
    U.redteam()
    (xtr, ytr), (xte, yte) = R.load_data()
    t0 = time.time()
    if arm == "real2":
        m = U.train_real2(seed, xtr, ytr, xte, yte)
    else:
        m = R.train(arm == "free", seed, xtr, ytr, xte, yte)
    acc = R.test_acc(m, xte, yte)
    rec = {"arm": arm, "seed": seed, "test_acc": acc, "seconds": round(time.time() - t0, 1),
           "threads": torch.get_num_threads(), "device": R.DEV, "torch": torch.__version__,
           "steps": R.STEPS, "smoke": R.SMOKE, "redteam": rt}
    out = HERE / JOB_FILE.format(arm=arm, seed=seed)
    out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"  {arm} seed {seed}: TEST ACC {acc:.4f}  ({rec['seconds']:.0f}s) -> {out.name}", flush=True)
    return out


def merge() -> int:
    """Exactly run_pmnist_untied.main's result dict, from the six job files."""
    assert not R.SMOKE
    jobs = {}
    for arm, s in JOBS:
        p = HERE / JOB_FILE.format(arm=arm, seed=s)
        assert p.exists(), f"missing job {p.name}"
        jobs[(arm, s)] = json.loads(p.read_text(encoding="utf-8"))
        assert jobs[(arm, s)]["steps"] == R.STEPS and not jobs[(arm, s)]["smoke"]
    res = {"prereg": U.PREREG.name,
           "config": {"task": "permuted-MNIST", "perm_seed": R.PERM_SEED, "T": R.T_LEN, "H": R.H,
                      "d_ssm": R.D_SSM, "blocks": R.N_BLK, "steps": R.STEPS, "seeds": R.SEEDS,
                      "device": R.DEV, "torch": torch.__version__, "smoke": R.SMOKE},
           "params": {"free": R.nparams(True), "clamped": R.nparams(False), "real2": U.nparams(U.RealClassifier())},
           "test_acc": {arm: [jobs[(arm, s)]["test_acc"] for s in R.SEEDS] for arm in ("free", "clamped", "real2")}}
    fa, ca, ra = (float(np.mean(res["test_acc"][a])) for a in ("free", "clamped", "real2"))
    metrics = {"anchor_max_abs_dev": round(max(abs(fa - U.ANCHORS["free"]), abs(ca - U.ANCHORS["clamped"])), 4),
               "gap_free_minus_clamped": round(fa - ca, 4),
               "free_minus_real2": round(fa - ra, 4),
               "real2_minus_clamped": round(ra - ca, 4),
               "recovery_fraction": round((ra - ca) / (fa - ca), 4) if fa != ca else None}
    res["means"] = {"free": round(fa, 4), "clamped": round(ca, 4), "real2": round(ra, 4)}
    res["metrics"] = metrics
    v = Experiment(U.PREREG, repo_root=U.ROOT).score(metrics, smoke=False)
    res["verdict"], res["gates"] = v.verdict, v.gates
    res["plumbing"] = {"runner": "run_pmnist_untied_fast.py", "what": __doc__.strip().splitlines()[0],
                       "sharded_jobs": [{"arm": a, "seed": s, "seconds": jobs[(a, s)]["seconds"],
                                         "threads": jobs[(a, s)]["threads"]} for a, s in JOBS],
                       "scan_redteam": jobs[JOBS[0]]["redteam"],
                       "anchors_gate_is_the_detector": "G_P_anchors"}
    out = HERE / "pmnist_untied_result.json"
    out.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\n  metrics:", json.dumps(metrics))
    print(f"\n===== VERDICT: {res['verdict']} =====\nwrote {out.name}")
    return 0


def main() -> int:
    a = sys.argv[1:]
    if a[:1] == ["--redteam"]:
        redteam()
        return 0
    if a[:1] == ["--job"]:
        run_job(a[1], int(a[2]))
        return 0
    if a[:1] == ["--merge"]:
        return merge()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
