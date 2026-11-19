"""PATH-2c, G-P3 (PREREG_path2c_git_door_2026_11_19): the text door over the G-P4 cases, written out so two trees
can be compared. Builds the cases with path2b_fuzz.py's generator and seed, making the same draws as its `--git`
run (so the cases are G-P4's), reads the summaries through `gate_diff_text` of the `styxx` under --styxx, over the
generator's diff and over `git diff` of the two-commit repository, and prints the sha256 of every (case, summary,
kind, verdict, reason) line, with the count. The git door is not run.

    python web/gate/differential/path2c_text_same.py --styxx DIR --cases 30000 --seed 3
"""
import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--styxx", required=True)
ap.add_argument("--cases", type=int, default=30000)
ap.add_argument("--seed", type=int, default=3)
a = ap.parse_args()
sys.path.insert(0, a.styxx)
import styxx.diffgate as dg  # noqa: E402  (loaded from --styxx before path2b_fuzz adds its own tree)
sys.path.insert(1, str(Path(__file__).resolve().parent))
import path2b_fuzz as fz  # noqa: E402

assert Path(dg.__file__).resolve().is_relative_to(Path(a.styxx).resolve()), dg.__file__


def text_doors(root, files, summs):
    """path2b_fuzz.doors without the git door: the text door over `git diff` of the same two-commit repository."""
    d = tempfile.mkdtemp(dir=root)
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")

    def g(*x):
        return subprocess.run(["git", "-C", d, *x], capture_output=True, text=True, env=env, check=True).stdout
    g("init", "-q")
    g("config", "user.email", "x@y")
    g("config", "user.name", "x")
    for p, b0, _b in files:
        Path(d, p).parent.mkdir(parents=True, exist_ok=True)
        Path(d, p).write_text("\n".join(b0) + "\n")
    g("add", "-A")
    g("commit", "-qm", "base")
    for p, _b0, b in files:
        Path(d, p).write_text("\n".join(b) + "\n")
    g("commit", "-qam", "head")
    text = g("diff", "HEAD~1..HEAD")
    return [(s, dg.gate_diff_text(s, text).claims, []) for s in summs]


fz.doors = text_doors                      # `one` draws the summaries before it calls doors, so the draws match
r = random.Random(a.seed)
h = hashlib.sha256()
cases = lines = made = 0
with tempfile.TemporaryDirectory() as root:
    while cases < a.cases:
        made += 1
        res = fz.one(r, made, root)
        if res is None:
            continue
        cases += 1
        _diff, out, git = res              # out: the generator's diff; git: `git diff`, every claim
        for summ, kind, verdict, why, _decided, _true in out:
            h.update(json.dumps([made, "diff", summ, kind, verdict, why]).encode() + b"\n")
            lines += 1
        for summ, claims, _k, _truths in git:
            for c in claims:
                h.update(json.dumps([made, "git", summ, c.kind, c.verdict, c.why]).encode() + b"\n")
                lines += 1
print(json.dumps({"styxx": dg.__file__, "cases": cases, "lines": lines, "sha256": h.hexdigest()}))
