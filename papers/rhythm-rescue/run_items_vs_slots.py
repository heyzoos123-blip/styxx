# -*- coding: utf-8 -*-
"""
run_items_vs_slots.py -- frozen by PREREG_items_vs_slots_2026_09_02 (rhythm-rescue).

WHAT DOES ROTATION BUY -- ITEMS, OR SLOTS? The parent arc showed the phase clamp costs 3.33 items of
copy capacity and untied real magnitudes recover 0.0 of it. If phase is an ORDER code, the clamped
bank should still HOLD the items and lose only their slots. This runner trains the parent's three
arms on the parent's task, unchanged, and scores the SAME predictions two ways:

  ORDER  -- position-by-position accuracy (the parent's score; the anchors)
  ITEMS  -- multiset overlap |bag(pred) & bag(target)| / K, chance-corrected per K against the
            input-blind bag baseline frozen in the preregistration

No task is chosen. Capacity is first-failure on the grid for both scores; evaluation draws are
seeded per (K, seed) so every arm is scored on identical trials.

  python run_items_vs_slots.py [--smoke]
"""
from __future__ import annotations
import sys, json, time
from pathlib import Path
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_rhythm_rescue as R                    # noqa: E402
import run_untied_control as U                   # noqa: E402

ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from styxx.protocol import Experiment            # noqa: E402

SMOKE = "--smoke" in sys.argv
PREREG = HERE / "PREREG_items_vs_slots_2026_09_02.md"
ANCHORS = {"free": 6.0, "clamped": 2.6667, "real2": 2.6667}     # rhythm_rescue_result.json#/gate, untied_control_result.json#/arms
STEPS = 200 if SMOKE else R.STEPS
SEEDS = [0] if SMOKE else R.SEEDS
KGRID = [1, 2, 4, 8] if SMOKE else R.KGRID
EVAL_N = 256 if SMOKE else 2048
ARMS = ("free", "clamped", "real2")
LAMBDA = (R.ACC_THR - 1.0 / R.V) / (1.0 - 1.0 / R.V)              # 0.78182: the order bar's chance-corrected level
# Input-blind bag baseline, frozen (Monte Carlo, 200000 draws per K, numpy seed 0; re-derived in redteam()).
BASE_ITEM = {1: 0.0836, 2: 0.1596, 3: 0.2298, 4: 0.294, 6: 0.4063, 8: 0.5015, 10: 0.5813, 12: 0.6482,
             15: 0.655, 18: 0.6772, 20: 0.6969}
THR_ITEM = {K: round(b + LAMBDA * (1 - b), 4) for K, b in BASE_ITEM.items()}


def base_item_mc(K, n=200000, seed=0):
    rng = np.random.default_rng(seed)
    syms = rng.integers(0, R.V, (n, K))
    counts = np.stack([(syms == v).sum(1) for v in range(R.V)], 1)
    bag = np.bincount(np.array([i % R.V for i in range(K)]), minlength=R.V)
    return round(float((np.minimum(counts, bag[None, :]).sum(1) / K).mean()), 4)


def make_batch_seeded(n, K, seed):
    g = torch.Generator().manual_seed(1_000_003 * K + seed)
    syms = torch.randint(0, R.V, (n, K), generator=g).to(R.DEV)
    inp = torch.cat([syms, torch.full((n, K), R.V, device=R.DEV)], 1)
    tgt = torch.full((n, 2 * K), -100, device=R.DEV)
    tgt[:, K:] = syms
    return inp, tgt


@torch.no_grad()
def scores(m, K, seed, n=EVAL_N):
    m.eval()
    inp, tgt = make_batch_seeded(n, K, seed)
    pred = m(inp).argmax(-1)[:, K:]
    truth = tgt[:, K:]
    order = (pred == truth).float().mean().item()
    cp = torch.stack([(pred == v).sum(1) for v in range(R.V)], 1)
    ct = torch.stack([(truth == v).sum(1) for v in range(R.V)], 1)
    items = (torch.minimum(cp, ct).sum(1).float() / K).mean().item()
    m.train()
    return round(order, 4), round(items, 4)


def kcap_first_failure(acc_by_K, thr_by_K):
    cap = 0
    for K in KGRID:
        if acc_by_K[K] >= thr_by_K[K]:
            cap = K
        else:
            break
    return cap


def kcap_largest(acc_by_K, thr):
    return max([K for K in KGRID if acc_by_K[K] >= thr], default=0)


def redteam():
    U.redteam()
    dev = max(abs(base_item_mc(K) - BASE_ITEM[K]) for K in BASE_ITEM) if not SMOKE else 0.0
    a, _ = make_batch_seeded(8, 5, 0); b, _ = make_batch_seeded(8, 5, 0); c, _ = make_batch_seeded(8, 5, 1)
    assert torch.equal(a, b) and not torch.equal(a, c)
    # the item score of a perfect prediction is 1 and of a shuffled one is 1 (items kept, slots lost)
    _, tgt = make_batch_seeded(4, 6, 0); truth = tgt[:, 6:]
    perm = truth[:, torch.randperm(6)]
    cp = torch.stack([(perm == v).sum(1) for v in range(R.V)], 1); ct = torch.stack([(truth == v).sum(1) for v in range(R.V)], 1)
    assert (torch.minimum(cp, ct).sum(1) == 6).all()
    print(f"  [redteam] baseline re-derived max|dev|={dev:.4f}; seeded draws reproduce; shuffled truth scores items=1", flush=True)
    return dev


def main() -> int:
    print(f"device={R.DEV} smoke={SMOKE} D={R.D} steps={STEPS} seeds={SEEDS} kgrid={KGRID} thr_item={THR_ITEM}", flush=True)
    base_dev = redteam()
    res = {"prereg": PREREG.name, "config": {"D": R.D, "V": R.V, "kmax": R.KMAX, "steps": STEPS, "seeds": SEEDS, "kgrid": KGRID,
                                              "acc_thr": R.ACC_THR, "lambda": round(LAMBDA, 5), "base_item": BASE_ITEM,
                                              "thr_item": THR_ITEM, "eval_n": EVAL_N, "device": R.DEV,
                                              "torch": torch.__version__, "smoke": SMOKE},
           "arms": {a: {"seeds": {}} for a in ARMS}}
    t0 = time.time(); rule_mismatch = 0
    for arm in ARMS:
        for s in SEEDS:
            m = U.train(arm, s) if not SMOKE else _train_smoke(arm, s)
            order, items = {}, {}
            for K in KGRID:
                order[K], items[K] = scores(m, K, s)
            ko = kcap_first_failure(order, {K: R.ACC_THR for K in KGRID})
            ki = kcap_first_failure(items, THR_ITEM)
            if ko != kcap_largest(order, R.ACC_THR):
                rule_mismatch += 1
            res["arms"][arm]["seeds"][str(s)] = {"order": order, "items": items, "kcap_order": ko, "kcap_items": ki}
            print(f"  {arm:8s} seed {s}: kcap_order {ko:2d} kcap_items {ki:2d}  ({time.time()-t0:.0f}s)", flush=True)
            del m
    for arm in ARMS:
        sd = res["arms"][arm]["seeds"]
        res["arms"][arm]["kcap_order_mean"] = round(float(np.mean([v["kcap_order"] for v in sd.values()])), 4)
        res["arms"][arm]["kcap_items_mean"] = round(float(np.mean([v["kcap_items"] for v in sd.values()])), 4)
        res["arms"][arm]["kcap_items_max"] = max(v["kcap_items"] for v in sd.values())
    fo, co, ro = (res["arms"][a]["kcap_order_mean"] for a in ARMS)
    fi, ci, ri = (res["arms"][a]["kcap_items_mean"] for a in ARMS)
    gap_order, gap_item = round(fo - co, 4), round(fi - ci, 4)
    metrics = {"anchor_max_abs_dev": round(max(abs(fo - ANCHORS["free"]), abs(co - ANCHORS["clamped"]), abs(ro - ANCHORS["real2"])), 4),
               "rule_mismatch": rule_mismatch, "baseline_max_abs_dev": round(base_dev, 4),
               "gap_order": gap_order, "free_items": fi, "free_items_max": res["arms"]["free"]["kcap_items_max"],
               "gap_items": gap_item, "interaction": round(gap_order - gap_item, 4),
               "real2_items_minus_clamped_items": round(ri - ci, 4), "free_minus_real2_order": round(fo - ro, 4)}
    res["metrics"] = metrics
    v = Experiment(PREREG, repo_root=ROOT).score(metrics, smoke=SMOKE)
    res["verdict"], res["gates"] = v.verdict, v.gates
    out = HERE / ("items_vs_slots_smoke.json" if SMOKE else "items_vs_slots_result.json")
    out.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\n  metrics:", json.dumps(metrics))
    print(f"\n===== VERDICT: {res['verdict']} =====\nwrote {out.name}")
    return 0


def _train_smoke(arm, seed):
    import torch.nn as nn
    torch.manual_seed(seed); np.random.seed(seed)
    m = (U.Real2Model() if arm == "real2" else R.Model(arm == "free")).to(R.DEV)
    opt = torch.optim.Adam(m.parameters(), lr=R.LR); lossf = nn.CrossEntropyLoss(ignore_index=-100)
    for _ in range(STEPS):
        K = int(np.random.randint(1, R.KMAX + 1)); inp, tgt = R.make_batch(R.BATCH, K)
        loss = lossf(m(inp).reshape(-1, R.V), tgt.reshape(-1)); opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
    return m


if __name__ == "__main__":
    sys.exit(main())
