# -*- coding: utf-8 -*-
"""styxx.sworn_preview — check a sworn document against the WORKING TREE before it is committed.

The verifier resolves ``path:`` and ``prereg:`` receipts at a commit, through git plumbing, never
a checkout: a verdict is a function of bytes, not of somebody's working copy. That is right for a
verdict and wrong for an author, who must otherwise commit the files a document cites, swear,
then commit the sidecar — and discover a mis-bound span one commit too late.

This module is the author's mirror, not a verifier: the same lexer, the same adjudication, the
same document verdicts, resolved against the files on disk, and

- it issues NO receipt and writes NO sidecar (nothing it prints can be committed as a verdict);
- the tree it resolves against names itself ``worktree`` in the commit field, so any output that
  escapes is recognisable as a preview and never mistaken for a receipt at a commit.

  python -m styxx.sworn_preview DOC.md [--repo .] [--manifest M.json]

Exit 0 on SWORN-HELD, 1 otherwise — so it can sit in a pre-commit hook.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple

from styxx.sworn import Manifest, _headline, _sha256, verify

__all__ = ["WorkTree", "preview", "main"]

WORKTREE = "worktree"


class WorkTree:
    """The files on disk under ``root``. Names itself ``worktree`` as its commit."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.commit = WORKTREE

    def blob(self, path: str) -> Tuple[Optional[bytes], str]:
        p = (self.root / path)
        try:
            rp = p.resolve()
        except OSError:
            return None, "path_absent"
        if self.root not in rp.parents and rp != self.root:
            return None, "path_absent"            # never read outside the tree
        if not rp.is_file():
            return None, "path_absent"
        return rp.read_bytes(), "ok"

    def find_sha256(self, digest: str) -> Tuple[Optional[bytes], str]:
        """Content-addressed receipts (``prereg:``) — search the documents on disk."""
        for p in sorted(self.root.glob("papers/**/*.md")):
            try:
                b = p.read_bytes()
            except OSError:
                continue
            if _sha256(b) == digest:
                return b, "ok"
        return None, "prereg_not_in_tree"


def preview(raw: bytes, *, name: str, repo, manifest: Optional[Manifest] = None) -> dict:
    core = verify(raw, name=name, manifest=manifest, tree=WorkTree(repo), commit=None)
    assert core["commit"] == WORKTREE
    return core


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="styxx.sworn_preview",
                                 description="author-side preview of a sworn document against the working tree")
    ap.add_argument("doc")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--manifest", default=None)
    a = ap.parse_args(argv)
    raw = Path(a.doc).read_bytes()
    mf = Manifest.load(a.manifest) if a.manifest else None
    core = preview(raw, name=Path(a.doc).name, repo=a.repo, manifest=mf)
    print("PREVIEW against the working tree — not a verdict, no receipt issued")
    print(_headline(core))
    for s in core["spans"]:
        if s["verdict"] != "HELD":
            print("  %-10s %-24s %s @%d %s" % (s["verdict"], s["reason"] or "", s["receipt"] or "",
                                              s["at"], (s.get("detail") or {}).get("printed", "")))
    for cl in core["coverage"]["unsworn_claims"][:20]:
        print("  UNSWORN-CLAIM? @%d: %s" % (cl["start"], cl["text"][:100]))
    return 0 if core["document_verdict"] == "SWORN-HELD" else 1


if __name__ == "__main__":
    sys.exit(main())
