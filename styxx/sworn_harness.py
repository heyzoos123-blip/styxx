# -*- coding: utf-8 -*-
"""styxx.sworn_harness — the harness side of sworn output for CODING work.

An agent that finishes a task writes a report: "the suite passes, three files changed, two
commits." Sworn output lets it bind each of those numbers to a receipt — but invariant 2 of
``sworn/0.1`` says receipts are harness-minted, never author-minted. This module is that harness
for the things a coding agent reports on: commands it ran, the diff it produced, the commits it
made. It mints a ``sworn/manifest/0.1`` manifest whose receipts are:

- for every command: its command line (``harness_note``, so the author can swear to WHAT was
  run), its stdout (``tool_stdout``, complete), its stderr (``tool_stderr``, complete) and its
  exit code (``harness_note``, complete);
- for the commands this harness knows how to read, scalars the HARNESS extracted — pytest's
  passed/failed/skipped counts (``test_report``), ``git diff --shortstat``'s files, insertions
  and deletions and ``git rev-list --count``'s commit count (``harness_note``), and for a
  re-derivation script run with ``--emit-json``, EVERY numeric leaf of the one JSON object it
  prints (``harness_note``) — the receipt a sworn REFUTATION binds to, so a referee's number is
  held to the same standard as the author's;
- for a diff: the full patch as a digest-only receipt (``tool_stdout``, complete, for ``hash``;
  the bytes re-derive from git at the two commits) and the changed-file list (``tool_stdout``,
  complete, for ``quote``/``absent``).

The gaming vector this design closes: extraction owned by the author. If the agent supplied the
regex that pulls "3 files changed" out of the output, it could supply one that finds the number it
wants. Here the extractor table is fixed in this file, keyed by the command's first tokens; a
command the harness does not know yields stdout, stderr and exit code only, and the author may
swear to those bytes (``hash``, ``quote``, ``absent``) or to the exit code (``numeric``) and to
nothing the harness did not itself read. Every receipt kind this module mints is in
``SOURCE_KINDS_EXTERNAL``; it cannot mint an author-side kind.

Beside the manifest it writes a legend — ``<manifest>.legend.json`` — saying what each ``rN``
is, so the author can pick the right receipt. The legend is harness-written and is not a
receipt; the verifier never reads it.

  python -m styxx.sworn_harness M.json new --turn ID
  python -m styxx.sworn_harness M.json exec -- pytest -q tests/test_sworn.py
  python -m styxx.sworn_harness M.json diff BASE HEAD
  python -m styxx.sworn_harness M.json commits BASE HEAD
  python -m styxx.sworn_harness M.json turn BASE HEAD --turn ID     # the standard turn, fixed order
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from styxx.sworn import SOURCE_KINDS_EXTERNAL, Manifest

__all__ = ["Harness", "EXTRACTORS", "extract_pytest", "extract_shortstat", "extract_count",
           "extract_rederive", "REDERIVE_FLAG", "main"]

HARNESS_NAME = "styxx/sworn_harness.py"


# --- extractors: fixed in this file, keyed by command shape, never supplied by the author -------

def extract_pytest(stdout: bytes, stderr: bytes) -> Dict[str, int]:
    """pytest's summary line, read the way harness_pytest.py reads it."""
    text = (stdout + stderr).decode("utf-8", errors="replace")
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    summary = lines[-1] if lines else ""
    # Always the same five keys in the same order, so the receipt ids a workflow mints are stable
    # from run to run and an author can write `rN` before the run exists.
    out = {"passed": 0, "failed": 0, "skipped": 0, "xfailed": 0, "errors": 0}
    for key in ("passed", "failed", "skipped", "xfailed", "error", "errors"):
        m = re.search(r"(\d+) %s\b" % key, summary)
        if m:
            out["errors" if key == "error" else key] = int(m.group(1))
    return out


def extract_shortstat(stdout: bytes, stderr: bytes) -> Dict[str, int]:
    """``git diff --shortstat``: '3 files changed, 10 insertions(+), 2 deletions(-)'."""
    text = stdout.decode("utf-8", errors="replace")
    out = {"files_changed": 0, "insertions": 0, "deletions": 0}
    m = re.search(r"(\d+) files? changed", text)
    if m:
        out["files_changed"] = int(m.group(1))
    m = re.search(r"(\d+) insertions?\(\+\)", text)
    if m:
        out["insertions"] = int(m.group(1))
    m = re.search(r"(\d+) deletions?\(-\)", text)
    if m:
        out["deletions"] = int(m.group(1))
    return out


def extract_count(stdout: bytes, stderr: bytes) -> Dict[str, int]:
    """``git rev-list --count``: one integer on stdout."""
    text = stdout.decode("utf-8", errors="replace").strip()
    return {"count": int(text)} if re.fullmatch(r"\d+", text) else {}


REDERIVE_FLAG = "--emit-json"
REDERIVE_CAP = 64


def extract_rederive(stdout: bytes, stderr: bytes) -> Dict[str, Any]:
    """A re-derivation script (``--emit-json``) prints one JSON object; every numeric leaf is
    minted, in document order, keyed by its JSON-pointer path — the harness records what the
    script printed, all of it, and the author chooses nothing about which numbers exist."""
    try:
        obj = json.loads(stdout.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}
    out: Dict[str, Any] = {}

    def walk(x, path):
        if len(out) >= REDERIVE_CAP:
            return
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            out[path] = x
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(v, path + "/" + str(k).replace("~", "~0").replace("/", "~1"))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, path + "/" + str(i))
    walk(obj, "")
    return out


def _is_rederive(argv: Sequence[str]) -> bool:
    return REDERIVE_FLAG in argv


def _is_pytest(argv: Sequence[str]) -> bool:
    return (argv[:1] == ["pytest"] or argv[:3] == [sys.executable, "-m", "pytest"]
            or (len(argv) >= 3 and argv[1:3] == ["-m", "pytest"]))


def _is_shortstat(argv: Sequence[str]) -> bool:
    return argv[:2] == ["git", "diff"] and "--shortstat" in argv


def _is_revcount(argv: Sequence[str]) -> bool:
    return argv[:2] == ["git", "rev-list"] and "--count" in argv


# (predicate, extractor, kind_of_source for the scalars it mints)
EXTRACTORS: List[Tuple[Callable[[Sequence[str]], bool], Callable[[bytes, bytes], Dict[str, Any]], str]] = [
    (_is_rederive, extract_rederive, "harness_note"),
    (_is_pytest, extract_pytest, "test_report"),
    (_is_shortstat, extract_shortstat, "harness_note"),
    (_is_revcount, extract_count, "harness_note"),
]


class Harness:
    """Mint receipts for commands, diffs and commit ranges into one turn manifest."""

    def __init__(self, path, turn: Optional[str] = None, cwd: Optional[str] = None):
        self.path = Path(path)
        self.cwd = str(cwd or Path.cwd())
        if self.path.exists():
            self.manifest = Manifest.load(self.path)
            self.legend = json.loads(self._legend_path().read_text(encoding="utf-8")) \
                if self._legend_path().exists() else {"legend": {}}
        else:
            if not turn:
                raise SystemExit("REFUSED: a new manifest needs --turn")
            self.manifest = Manifest(harness=HARNESS_NAME, turn=turn)
            self.legend = {"legend": {}}

    # -- receipts -------------------------------------------------------------------------------
    def _legend_path(self) -> Path:
        return self.path.with_name(self.path.name[:-len(".json")] + ".legend.json"
                                   if self.path.name.endswith(".json") else self.path.name + ".legend.json")

    def _next_id(self) -> str:
        n = max((int(k[1:]) for k in self.manifest.receipts), default=0) + 1
        return "r%d" % n

    def _mint(self, data: bytes, kind: str, what: str, digest_only: bool = False) -> str:
        assert kind in SOURCE_KINDS_EXTERNAL, kind          # this harness cannot mint author kinds
        rid = self._next_id()
        if digest_only:
            # bytes the reader can re-derive (a patch between two commits) ride as a digest, so
            # `hash` verifies and the manifest stays small; `quote`/`absent` need bytes and get none
            self.manifest.add(rid, None, kind, complete=True, sha256=hashlib.sha256(data).hexdigest())
        else:
            self.manifest.add(rid, data, kind, complete=True)
        self.legend["legend"][rid] = {"kind_of_source": kind, "what": what, "digest_only": digest_only}
        return rid

    def save(self) -> Path:
        self.manifest.write(self.path)
        self.legend["manifest"] = self.path.name
        self.legend["harness"] = HARNESS_NAME
        self.legend["note"] = ("harness-written; not a receipt; the verifier never reads it. "
                               "Every scalar here was extracted by styxx.sworn_harness's fixed "
                               "extractor table, never by the author.")
        self._legend_path().write_text(json.dumps(self.legend, indent=1) + "\n", encoding="utf-8")
        return self.path

    # -- steps ----------------------------------------------------------------------------------
    def exec(self, argv: Sequence[str], timeout: Optional[float] = None) -> Dict[str, str]:
        """Run ``argv`` in cwd; mint stdout, stderr, exit code, and any harness-extracted scalars."""
        argv = list(argv)
        r = subprocess.run(argv, cwd=self.cwd, capture_output=True, check=False, timeout=timeout)
        label = " ".join(argv)
        # The command line itself, minted by the harness, so an author can swear to WHAT was run
        # (`k="quote"` against it) and a reader can tell the suite from three chosen tests.
        ids = {"argv": self._mint(label.encode("utf-8"), "harness_note", "command line of: %s" % label),
               "stdout": self._mint(r.stdout, "tool_stdout", "stdout of: %s" % label),
               "stderr": self._mint(r.stderr, "tool_stderr", "stderr of: %s" % label),
               "exit_code": self._mint(str(r.returncode).encode("ascii"), "harness_note",
                                       "exit code of: %s" % label)}
        for pred, fn, kind in EXTRACTORS:
            if pred(argv):
                for name, val in fn(r.stdout, r.stderr).items():
                    ids[name] = self._mint(json.dumps(val).encode("ascii"), kind,
                                           "%s, extracted by the harness from: %s" % (name, label))
                break
        return ids

    def diff(self, base: str, head: str) -> Dict[str, str]:
        """Mint the shortstat scalars, the full patch (for hash) and the changed-file list."""
        ids = self.exec(["git", "diff", "--shortstat", base, head])
        patch = subprocess.run(["git", "diff", base, head], cwd=self.cwd, capture_output=True, check=False)
        names = subprocess.run(["git", "diff", "--name-only", base, head], cwd=self.cwd,
                               capture_output=True, check=False)
        ids["patch"] = self._mint(patch.stdout, "tool_stdout",
                                  "git diff %s %s (full patch, digest only; re-derive with git)" % (base, head),
                                  digest_only=True)
        ids["names"] = self._mint(names.stdout, "tool_stdout", "git diff --name-only %s %s" % (base, head))
        return ids

    def standard(self, base: str, head: str, *, ruff_argv: Optional[Sequence[str]] = None,
                 pytest_argv: Optional[Sequence[str]] = None) -> Dict[str, Dict[str, str]]:
        """THE STANDARD TURN — the order the workflow, the README's receipt map and a local author
        all share, so an `rN` written before the run exists names the same bytes in CI:
        commits (r1-r6), diff (r7-r15), ruff (r16-r19), pytest (r20-r28)."""
        assert not self.manifest.receipts, "standard() mints into a fresh manifest only"
        ruff_argv = list(ruff_argv or [sys.executable, "-m", "ruff", "check", "styxx"])
        pytest_argv = list(pytest_argv or [sys.executable, "-m", "pytest", "tests", "-q", "--no-header",
                                           "-p", "no:cacheprovider", "--tb=line"])
        return {"commits": self.commits(base, head), "diff": self.diff(base, head),
                "ruff": self.exec(ruff_argv), "pytest": self.exec(pytest_argv)}

    def commits(self, base: str, head: str) -> Dict[str, str]:
        """Mint the commit count and the list of commit ids in base..head."""
        ids = self.exec(["git", "rev-list", "--count", "%s..%s" % (base, head)])
        lst = subprocess.run(["git", "rev-list", "%s..%s" % (base, head)], cwd=self.cwd,
                             capture_output=True, check=False)
        ids["list"] = self._mint(lst.stdout, "tool_stdout", "git rev-list %s..%s" % (base, head))
        return ids


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="styxx.sworn_harness",
                                 description="harness-side receipts for a coding agent's report")
    ap.add_argument("manifest")
    ap.add_argument("--cwd", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("--turn", required=True)
    e = sub.add_parser("exec")
    e.add_argument("argv", nargs=argparse.REMAINDER)
    d = sub.add_parser("diff")
    d.add_argument("base")
    d.add_argument("head")
    c = sub.add_parser("commits")
    c.add_argument("base")
    c.add_argument("head")
    s = sub.add_parser("turn", help="the standard turn: commits, diff, ruff, pytest in the fixed order")
    s.add_argument("base")
    s.add_argument("head")
    s.add_argument("--turn", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "new":
        h = Harness(a.manifest, turn=a.turn, cwd=a.cwd)
        if h.path.exists():
            raise SystemExit("REFUSED: %s exists; extend it with exec/diff/commits" % h.path)
        h.save()
        print("minted %s for turn %s" % (h.path.name, a.turn))
        return 0
    if a.cmd == "turn":
        h = Harness(a.manifest, turn=a.turn, cwd=a.cwd)
        if h.manifest.receipts:
            raise SystemExit("REFUSED: turn mints into a fresh manifest; %s already holds receipts" % h.path)
        groups = h.standard(a.base, a.head)
        h.save()
        for g, ids in groups.items():
            for k, v in ids.items():
                print("%s\t%s.%s\t%s" % (v, g, k, h.legend["legend"][v]["what"]))
        return 0
    h = Harness(a.manifest, cwd=a.cwd)
    if a.cmd == "exec":
        cmd = [x for x in a.argv if x != "--"] if a.argv[:1] == ["--"] else a.argv
        if not cmd:
            raise SystemExit("REFUSED: exec needs a command after --")
        ids = h.exec(cmd)
    elif a.cmd == "diff":
        ids = h.diff(a.base, a.head)
    else:
        ids = h.commits(a.base, a.head)
    h.save()
    for k, v in ids.items():
        print("%s\t%s\t%s" % (v, k, h.legend["legend"][v]["what"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
