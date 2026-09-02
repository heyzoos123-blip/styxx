# -*- coding: utf-8 -*-
"""styxx.referee — sworn refutation, checked and indexed.

A refutation is a set of numbers aimed at a sworn document. This lab holds the critic to the
author's standard: the numbers must come from a re-derivation script the harness ran
(``styxx.sworn_harness`` with ``--emit-json`` mints every numeric leaf the script prints), the
document must swear to those receipts, and it must bind to the document it attacks by quoting
that document's own bytes at the commit. This module ACCEPTS or REJECTS a refutation on those
terms and indexes which documents are contested and by what. It never judges who is right —
the verifier already did that for every number — it judges whether the argument is checkable.

A refutation is ACCEPTED iff, at the commit its sidecar names:
1. it verifies SWORN-HELD with no UNRESOLVED span (every number binds, every binding resolves);
2. it has at least one target: a ``path:`` receipt into a committed ``.md`` document, quoted
   (``k="quote"``) — the refutation names what it attacks by the target's own bytes;
3. every ``.py`` path in a quoted harness command line (a receipt whose bytes are the command
   line the harness ran) exists at that commit — the re-derivation is reproducible from the tree;
4. at least one span binds to a manifest receipt (``rN``) — some number came through the harness.

  python -m styxx.referee check  papers/.../REFUTATION_x.sworn.json [--repo .]
  python -m styxx.referee index  [--repo .]
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from styxx.sworn import GitTree, Manifest, _parse_receipt, load_sidecar, verify

__all__ = ["check", "index", "main"]

REFUTATION_GLOB = "papers/**/REFUTATION_*.sworn.json"
ACCEPTED, REJECTED = "ACCEPTED", "REJECTED"
_PY = re.compile(r"(?<![\w/.-])([\w./-]+\.py)\b")


def _needle(raw: bytes, span: dict) -> Optional[str]:
    inner = raw[span["start"]:span["end"]]
    m = re.search(rb"`([^`\n]+)`", inner)
    return m.group(1).decode("utf-8", "replace") if m else None


def check(sidecar_obj: dict, repo=".") -> dict:
    side = load_sidecar(sidecar_obj)
    commit = side["commit"]
    reasons: List[str] = []
    if not commit:
        return {"status": REJECTED, "reasons": ["no_commit"], "targets": [], "scripts": [], "commit": None}
    tree = GitTree(repo, commit)
    core = verify(sidecar=side, tree=tree)
    if core["document_verdict"] != "SWORN-HELD":
        reasons.append("not_sworn_held:%s" % core["document_verdict"])
    if core["counts"].get("UNRESOLVED"):
        reasons.append("unresolved_spans:%d" % core["counts"]["UNRESOLVED"])
    from styxx.sworn import render
    raw = render(side)
    manifest = Manifest.from_dict(side["manifest"]) if side.get("manifest", {}).get("receipts") else None
    targets, scripts, rn_bound = [], [], 0
    for s in core["spans"]:
        parsed, _ = _parse_receipt(s["receipt"])
        if not parsed:
            continue
        if parsed["form"] == "rn":
            rn_bound += 1
            if manifest and s["kind"] == "quote":
                e = manifest.receipts.get(parsed["id"])
                if e and e.get("kind_of_source") == "harness_note" and e.get("bytes"):
                    cmd = base64.b64decode(e["bytes"]).decode("utf-8", "replace")
                    for p in _PY.findall(cmd):
                        scripts.append(p)
        elif parsed["form"] == "path" and parsed["target"].endswith(".md") and s["kind"] == "quote":
            targets.append(parsed["target"])
    targets = sorted(set(targets)); scripts = sorted(set(scripts))
    if not targets:
        reasons.append("no_target_quoted")
    if not rn_bound:
        reasons.append("no_harness_receipt_bound")
    for p in scripts:
        blob, why = tree.blob(p)
        if blob is None:
            reasons.append("script_not_at_commit:%s:%s" % (p, why))
    return {"status": ACCEPTED if not reasons else REJECTED, "reasons": reasons, "targets": targets,
            "scripts": scripts, "commit": commit, "document": side["document"]["name"],
            "held": core["counts"].get("HELD", 0)}


def index(repo=".") -> Dict[str, List[dict]]:
    """target document -> the refutations that bind to it, each with its status."""
    root = Path(repo)
    out: Dict[str, List[dict]] = {}
    for sc in sorted(root.glob(REFUTATION_GLOB)):
        obj = json.loads(sc.read_text(encoding="utf-8"))
        r = check(obj, repo)
        for t in r["targets"] or ["(no target)"]:
            out.setdefault(t, []).append({"refutation": str(sc.relative_to(root))[:-len(".sworn.json")] + ".md",
                                          "status": r["status"], "reasons": r["reasons"], "commit": r["commit"]})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="styxx.referee", description="sworn refutation: check one, or index the tree")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("sidecar")
    c.add_argument("--repo", default=".")
    i = sub.add_parser("index")
    i.add_argument("--repo", default=".")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        r = check(json.loads(Path(a.sidecar).read_text(encoding="utf-8")), a.repo)
        print("%s  %s  held=%d  targets=%s  scripts=%s%s" % (r["status"], r["document"], r["held"], r["targets"],
                                                             r["scripts"], ("  " + ", ".join(r["reasons"])) if r["reasons"] else ""))
        return 0 if r["status"] == ACCEPTED else 1
    idx = index(a.repo)
    for t, rs in idx.items():
        print(t)
        for r in rs:
            print("  %-8s %s%s" % (r["status"], r["refutation"], ("  " + ", ".join(r["reasons"])) if r["reasons"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
