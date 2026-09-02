# -*- coding: utf-8 -*-
"""styxx.sworn_gate — the merge gate that reads a sworn pull-request description.

The deployment ``papers/sworn/DESIGN_agent_that_swears_2026_09_02.md`` describes: CI mints a
manifest on the pull-request head with ``styxx.sworn_harness`` (the agent has no write access
there), and this gate verifies the description against it. Policy, stated once:

- ``SWORN-HELD``   → pass. Every bound number is what a tool printed or a file holds.
- ``SWORN-FAILED`` → fail. The receipt names the span.
- ``MALFORMED``    → fail. A tag-shaped thing that is not the format is refused, never ignored.
- ``UNSWORN``      → neutral by default: exit 0 with a loud notice. A description that committed to
                     nothing is not "no failures", and the gate says so; ``--strict`` makes it fail,
                     which is the adoption switch a repository flips when its authors swear.

The gate never proposes tags, never edits the description, never picks receipts. It prints the
manifest's legend so an author can see which ``rN`` holds what, and writes the verdict receipt.

  python -m styxx.sworn_gate BODY.md --manifest M.json [--repo . --commit SHA] [--out receipt.json] [--strict]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple

from styxx.sworn import Manifest, issue_receipt, verify, _load_tree

__all__ = ["decide", "gate", "main"]

PASS, FAIL, NEUTRAL = "PASS", "FAIL", "NEUTRAL"


def decide(document_verdict: str, counts: Optional[dict] = None, strict: bool = False) -> str:
    """The policy table. One place, so a reader can audit it.

    The verifier's SWORN-HELD tolerates UNRESOLVED spans (it could not see; that is not an
    accusation). A merge gate cannot: a description swearing to receipts that do not exist in this
    manifest or at this commit is NEUTRAL, and FAIL under --strict, never PASS.
    """
    unresolved = int((counts or {}).get("UNRESOLVED", 0))
    if document_verdict == "SWORN-HELD":
        if unresolved:
            return FAIL if strict else NEUTRAL
        return PASS
    if document_verdict == "UNSWORN":
        return FAIL if strict else NEUTRAL
    return FAIL          # SWORN-FAILED, MALFORMED, anything the verifier refused


def gate(raw: bytes, *, name: str, manifest: Optional[Manifest], repo: Optional[str],
         commit: Optional[str], strict: bool = False) -> Tuple[str, dict]:
    tree = _load_tree(repo, commit) if repo else None
    core = verify(raw, name=name, manifest=manifest, tree=tree, commit=commit)
    return decide(core["document_verdict"], core["counts"], strict), core


def _legend_for(manifest_path: Path) -> Optional[dict]:
    lp = manifest_path.with_name(manifest_path.name[:-len(".json")] + ".legend.json") \
        if manifest_path.name.endswith(".json") else None
    if lp and lp.exists():
        try:
            return json.loads(lp.read_text(encoding="utf-8")).get("legend")
        except (OSError, ValueError):
            return None
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="styxx.sworn_gate", description="merge gate over a sworn PR description")
    ap.add_argument("body")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--repo", default=None)
    ap.add_argument("--commit", default=None)
    ap.add_argument("--out", default=None, help="write the verdict receipt JSON here")
    ap.add_argument("--strict", action="store_true", help="UNSWORN fails instead of passing with a notice")
    a = ap.parse_args(argv)
    raw = Path(a.body).read_bytes()
    manifest = Manifest.load(a.manifest) if a.manifest else None
    status, core = gate(raw, name=Path(a.body).name, manifest=manifest, repo=a.repo,
                        commit=a.commit, strict=a.strict)
    dv, counts = core["document_verdict"], core["counts"]
    print("sworn-gate: %s  (%s; %s)" % (status, dv, ", ".join("%s=%d" % kv for kv in counts.items())))
    for s in core["spans"]:
        if s["verdict"] != "HELD":
            print("  %-10s %-24s %s @%d" % (s["verdict"], s["reason"] or "", s["receipt"] or "", s["at"]))
    if dv == "UNSWORN":
        print("  NOTICE: this description swears to nothing. UNSWORN is not 'no failures'.%s"
              % ("" if a.strict else " Passing under the non-strict policy."))
    if counts.get("UNRESOLVED"):
        print("  NOTICE: %d span(s) name a receipt this manifest or commit does not hold; the gate "
              "cannot see them and does not pass them.%s"
              % (counts["UNRESOLVED"], "" if a.strict else " Neutral under the non-strict policy."))
    if a.manifest:
        legend = _legend_for(Path(a.manifest))
        if legend:
            print("  legend (what each rN holds):")
            for rid, e in legend.items():
                print("    %-4s %-13s %s" % (rid, e.get("kind_of_source", ""), e.get("what", "")[:90]))
    if a.out:
        rec = issue_receipt(core)
        rec_out = {"gate": status, "strict": bool(a.strict), "receipt": rec}
        Path(a.out).write_text(json.dumps(rec_out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("  receipt %s -> %s" % (rec["digest"][:12], a.out))
    return 0 if status in (PASS, NEUTRAL) else 1


if __name__ == "__main__":
    sys.exit(main())
