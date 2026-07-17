#!/usr/bin/env python3
"""
overconfidence_grounding_eval.py
================================

Mechanism validation for reference-grounded overconfidence (2026-06-15).

Text-only overconfidence scores the confidence REGISTER and is a documented
construct ceiling: it fires equally on confident-correct and confident-wrong
text, so it cannot measure miscalibration. The grounded combiner
(`styxx.mcp.server._grounded_overconfidence`) multiplies the register by a
WRONGNESS signal (P the response contradicts a correct_reference, which is
deception_v2's NLI contradiction probability):

    grounded_overconfidence = register × contradiction

This script validates the COMBINATION on the N=50 factual triples
(scripts/validation/deception_v2_factual_triples.py). Each triple gives a
confident TRUTH and a confident LIE for the same prompt. We use the triple
labels as a ground-truth contradiction oracle (truth → 0, lie → 1) so the
result isolates the combiner: the live contradiction signal is deception_v2's
job (NLI AUC 0.818) and is validated separately.

Expected: text-only register AUC ≈ 0.5 (chance — both sides are confident);
grounded register×wrongness AUC ≈ 1.0 (confident-wrong separates cleanly from
confident-correct).

    STYXX_SKIP_SHA=1 python scripts/self_audit/overconfidence_grounding_eval.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from styxx.attack import score_all  # noqa: E402
from styxx.mcp.server import _grounded_overconfidence  # noqa: E402
from scripts.validation.deception_v2_factual_triples import TRIPLES  # noqa: E402


def _auc(pos: list[float], neg: list[float]) -> float:
    wins = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return wins / (len(pos) * len(neg))


def main() -> int:
    reg_truth, reg_lie = [], []
    for prompt, truth, lie in TRIPLES:
        reg_truth.append(float(score_all(prompt=prompt, response=truth).get("overconfidence", 0.0)))
        reg_lie.append(float(score_all(prompt=prompt, response=lie).get("overconfidence", 0.0)))

    # ground-truth contradiction oracle: truth does not contradict (0), lie does (1)
    go_truth = [_grounded_overconfidence(r, 0.0) for r in reg_truth]
    go_lie = [_grounded_overconfidence(r, 1.0) for r in reg_lie]

    text_auc = _auc(reg_lie, reg_truth)
    grounded_auc = _auc(go_lie, go_truth)

    out = {
        "n_triples": len(TRIPLES),
        "text_only_register": {
            "auc_lie_vs_truth": round(text_auc, 4),
            "mean_truth": round(sum(reg_truth) / len(reg_truth), 4),
            "mean_lie": round(sum(reg_lie) / len(reg_lie), 4),
        },
        "grounded_register_x_wrongness": {
            "auc_lie_vs_truth": round(grounded_auc, 4),
            "mean_truth": round(sum(go_truth) / len(go_truth), 4),
            "mean_lie": round(sum(go_lie) / len(go_lie), 4),
        },
        "note": (
            "contradiction signal is a ground-truth oracle here; live "
            "contradiction = deception_v2 NLI (AUC 0.818, backend-gated)."
        ),
    }
    out_dir = _REPO_ROOT / "papers" / "agent-self-audit" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "overconfidence_grounding_eval.json").write_text(json.dumps(out, indent=2))

    print(f"n triples: {len(TRIPLES)}")
    print(f"text-only register   AUC(lie>truth): {text_auc:.4f}  "
          f"(mean truth {out['text_only_register']['mean_truth']} / lie {out['text_only_register']['mean_lie']})")
    print(f"grounded reg×wrongness AUC:          {grounded_auc:.4f}  "
          f"(mean truth {out['grounded_register_x_wrongness']['mean_truth']} / lie {out['grounded_register_x_wrongness']['mean_lie']})")
    print("wrote papers/agent-self-audit/results/overconfidence_grounding_eval.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
