"""PATH-2b, G-P4 (PREREG_path2b_changed_def_2026_11_19): a generated differential for R-101b.

Builds base and head Python files from the probe families of the plan and random edits, writes the diff of the two
(difflib, in git's header form, at several context sizes), reads summaries of `tests_added` and `symbol_added` claims
through the text door, and scores every verdict R-101b decides (a reason ending "(#101)") against the truth of the
plan's section 2, read by CPython's `ast` from the two files. The truth here is this file's own `ast` walk, written
apart from the gate's.

    python web/gate/differential/path2b_fuzz.py --cases 30000 --seed 1 [--out report.json] [--git 300]

--git N also runs N of the cases through the git door (`gate_diff` on a two-commit repository) and through the text
door over `git diff`, to count where the doors differ wherever the text door decides (G-P3 as amended at signing).
Prints one JSON object: cases, claims read, decisions by kind, decisions that differ from truth (with up to six
written out), and the Python version.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from styxx.diffgate import gate_diff, gate_diff_text  # noqa: E402

NAMES = ["test_a", "test_b", "test_c", "test_run", "test_basic", "test_x", "test_new", "test_old"]
CLASSES = ["TestA", "TestB", "TestFoo", "Helper"]
HELPERS = ["backoff", "close", "make", "setup_x"]


def truth(path: str, src: str):
    """{(path, classes, name): kinds}, or None where CPython does not parse the file."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    out: dict = {}

    def walk(node, classes):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.ClassDef):
                out.setdefault((path, classes, ch.name), set()).add("class")
                walk(ch, classes + (ch.name,))
            elif isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.setdefault((path, classes, ch.name), set()).add("function")
                walk(ch, classes)
            else:
                walk(ch, classes)
    walk(tree, ())
    return out


# ---- the files: a list of blocks, each a list of lines ----------------------------------------------------------

def body(r: random.Random, ind: str) -> list:
    pick = r.random()
    if pick < 0.5:
        return [ind + "    assert True"]
    if pick < 0.6:
        return [ind + '    """A docstring."""', ind + "    assert True"]
    if pick < 0.7:
        return [ind + '    s = """', ind + "def test_fake():", '"""', ind + "    assert s"]
    if pick < 0.78:
        return [ind + "    x = 'def test_y():'", ind + "    assert x"]
    if pick < 0.84:
        return [ind + '    v = f"{1 + 2}"', ind + "    assert v"]
    if pick < 0.9:
        return [ind + "    # def test_z(): a comment", ind + "    assert True"]
    if pick < 0.95:
        return [ind + "    def test_inner():", ind + "        pass", ind + "    assert test_inner"]
    return [ind + "    y = (1,", ind + "         2)", ind + "    assert y"]


def func(r: random.Random, name: str, ind: str = "", asyn: bool = False) -> list:
    lines = []
    if r.random() < 0.15:
        lines.append(ind + "@pytest.mark.slow")
    args = "self" if ind else ""
    if r.random() < 0.1:
        lines.append(ind + f"{'async ' if asyn else ''}def {name}(")
        lines.append(ind + f"    {args or 'x'}=None,")
        lines.append(ind + "):")
    else:
        lines.append(ind + f"{'async ' if asyn else ''}def {name}({args}):")
    return lines + body(r, ind)


def make_file(r: random.Random) -> list:
    """Blocks: ('def', classes, name, lines) or ('class', name, [blocks]) or ('other', lines)."""
    blocks = []
    if r.random() < 0.3:
        blocks.append(("other", ['"""Module docstring."""']))
    if r.random() < 0.5:
        blocks.append(("other", ["import pytest"]))
    for _ in range(r.randint(1, 6)):
        k = r.random()
        if k < 0.45:
            nm = r.choice(NAMES)
            blocks.append(("def", nm, r.random() < 0.08, func(r, nm)))
        elif k < 0.55:
            nm = r.choice(HELPERS)
            blocks.append(("def", nm, False, func(r, nm)))
        elif k < 0.85:
            inner = []
            for _ in range(r.randint(1, 3)):
                nm = r.choice(NAMES + HELPERS[:1])
                inner.append(("def", nm, r.random() < 0.05, func(r, nm, "    ")))
            blocks.append(("class", r.choice(CLASSES), inner))
        else:
            blocks.append(("other", [r.choice(["X = 1", "Y = {'a': 1}", "Z = '''multi", "line'''",
                                               "W = [", "    1,", "]"])]))
    return blocks


def render(blocks: list) -> list:
    out = []
    for b in blocks:
        if out:
            out += ["", ""]
        if b[0] == "def":
            out += b[3]
        elif b[0] == "class":
            out.append(f"class {b[1]}:")
            for i, d in enumerate(b[2]):
                if i:
                    out.append("")
                out += d[3]
        else:
            out += b[1]
    return out


def regen(r: random.Random, d, ind=""):
    """The same definition with its signature or body changed (a changed test, not an added one)."""
    nm = d[1]
    lines = list(d[3])
    i = next(k for k, x in enumerate(lines) if x.lstrip().startswith(("def ", "async def ")))
    if lines[i].endswith("):"):
        lines[i] = lines[i][:-2] + (", tmp_path):" if not lines[i].endswith("():") else "tmp_path):")
    else:
        lines[i] = lines[i] + "  # changed"
    return (d[0], nm, d[2], lines)


def edit(r: random.Random, blocks: list) -> list:
    """One to three random edits, from the families the plan lists."""
    b = [(x[0], x[1], [y for y in x[2]]) if x[0] == "class" else x for x in blocks]
    for _ in range(r.randint(1, 3)):
        defs = [(i, None) for i, x in enumerate(b) if x[0] == "def"]
        defs += [(i, j) for i, x in enumerate(b) if x[0] == "class" for j in range(len(x[2]))]
        k = r.random()
        if defs and k < 0.3:                                 # change a definition in place
            i, j = r.choice(defs)
            if j is None:
                b[i] = regen(r, b[i])
            else:
                b[i][2][j] = regen(r, b[i][2][j], "    ")
        elif k < 0.5:                                        # add a test, maybe one of a name already used
            nm = r.choice(NAMES)
            pos = r.randint(0, len(b))
            if r.random() < 0.5 and any(x[0] == "class" for x in b):
                ci = r.choice([i for i, x in enumerate(b) if x[0] == "class"])
                b[ci][2].insert(r.randint(0, len(b[ci][2])), ("def", nm, False, func(r, nm, "    ")))
            else:
                b.insert(pos, ("def", nm, r.random() < 0.1, func(r, nm)))
        elif defs and k < 0.62:                              # delete one
            i, j = r.choice(defs)
            if j is None:
                b.pop(i)
            else:
                b[i][2].pop(j)
                if not b[i][2]:
                    b[i][2].append(("def", "test_keep", False, func(r, "test_keep", "    ")))
        elif defs and k < 0.72:                              # rename one
            i, j = r.choice(defs)
            nm = r.choice(NAMES)
            src = b[i] if j is None else b[i][2][j]
            old = src[1]
            new = (src[0], nm, src[2], [x.replace(f"def {old}(", f"def {nm}(") for x in src[3]])
            if j is None:
                b[i] = new
            else:
                b[i][2][j] = new
        elif k < 0.8 and any(x[0] == "class" for x in b):   # rename a class
            ci = r.choice([i for i, x in enumerate(b) if x[0] == "class"])
            b[ci] = ("class", r.choice(CLASSES), b[ci][2])
        elif defs and k < 0.9:                               # move a test between a class and module level
            i, j = r.choice(defs)
            if j is not None:
                d = b[i][2].pop(j)
                if not b[i][2]:
                    b[i][2].append(("def", "test_keep", False, func(r, "test_keep", "    ")))
                b.insert(r.randint(0, len(b)), ("def", d[1], d[2], [x[4:] if x.startswith("    ") else x
                                                                  for x in d[3]]))
            else:
                d = b.pop(i)
                cls = [ci for ci, x in enumerate(b) if x[0] == "class"]
                if cls:
                    ci = r.choice(cls)
                    b[ci][2].append(("def", d[1], d[2], ["    " + x if x else x for x in func(r, d[1])]))
                else:
                    b.insert(0, d)
        else:                                                # an unrelated line at the top
            b.insert(0, ("other", [r.choice(["import os", "A = 1", "# a comment"])]))
    return b


def udiff(path: str, a: list, b: list, n: int) -> str:
    out = list(difflib.unified_diff(a, b, f"a/{path}", f"b/{path}", n=n, lineterm=""))
    if not out:
        return ""
    return f"diff --git a/{path} b/{path}\n" + "\n".join(out) + "\n"


def summaries(r: random.Random, got_max: int, names: list) -> list:
    s = [f"Added {n} test{'s' if n != 1 else ''}." for n in range(0, got_max + 2)]
    s += [f"Adds function {nm}." for nm in names]
    return s


def score(base: dict, head: dict, claim) -> bool | None:
    """Whether a decided verdict is true by the truth (None where truth cannot read the files)."""
    if claim.kind == "tests_added":
        added = {q for q, k in head.items() if q[2].startswith("test_") and "function" in k
                 and not (q in base and "function" in base[q])}
        return len(added) == int(claim.detail["n"])
    name = claim.detail["name"]
    return any(q[2] == name and q not in base for q in head)


def one(r: random.Random, case: int, git_dir: str | None):
    files = []
    for f in range(r.choice([1, 1, 1, 2])):
        path = f"tests/test_{f}.py"
        blocks = make_file(r)
        a = render(blocks)
        b = render(edit(r, blocks))
        if r.random() < 0.3:                                 # a long tail of unchanged tests below
            tail = render(make_file(random.Random(case * 7 + f)))
            a, b = a + ["", ""] + tail, b + ["", ""] + tail
        files.append((path, a, b))
    if len(files) == 2 and r.random() < 0.3:                 # a test moved to the other file
        p0, a0, b0 = files[0]
        p1, a1, b1 = files[1]
        files[1] = (p1, a1, b1 + ["", "", "def test_moved():", "    assert True"])
        files[0] = (p0, a0 + ["", "", "def test_moved():", "    assert True"], b0)
    n = r.choice([0, 1, 3, 3, 5, 100000])
    diff = "".join(udiff(p, a, b, n) for p, a, b in files)
    if not diff:
        return None
    base_t, head_t = {}, {}
    for p, a, b in files:
        ta, tb = truth(p, "\n".join(a) + "\n"), truth(p, "\n".join(b) + "\n")
        if ta is None or tb is None:
            return None
        base_t.update(ta)
        head_t.update(tb)
    got_max = sum(1 for line in diff.split("\n") if line.startswith("+") and "def test_" in line)
    names = sorted({q[2] for q in head_t if not q[2].startswith("test_")})[:2]
    out = []
    for summ in summaries(r, got_max, names):
        g = gate_diff_text(summ, diff)
        for c in g.claims:
            if c.kind not in ("tests_added", "symbol_added"):
                continue
            decided = c.verdict == "VERIFIED" and c.why.endswith("(#101)")
            out.append((summ, c.kind, c.verdict, c.why, decided, score(base_t, head_t, c) if decided else None))
    git = None
    if git_dir is not None:
        git = [(s, t, k, [score(base_t, head_t, c) if c.why.endswith("(#101)") and c.verdict == "VERIFIED"
                          else None for c in k])
               for s, t, k in doors(git_dir, files, summaries(r, got_max, names))]
    return diff, out, git


def doors(root: str, files: list, summs: list) -> list:
    """(summary, text door over `git diff`, git door) for each summary, on a two-commit repository."""
    d = tempfile.mkdtemp(dir=root)
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")

    def g(*a):
        return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=env, check=True).stdout
    g("init", "-q")
    g("config", "user.email", "x@y")
    g("config", "user.name", "x")
    for p, a, _b in files:
        Path(d, p).parent.mkdir(parents=True, exist_ok=True)
        Path(d, p).write_text("\n".join(a) + "\n")
    g("add", "-A")
    g("commit", "-qm", "base")
    for p, _a, b in files:
        Path(d, p).write_text("\n".join(b) + "\n")
    g("commit", "-qam", "head")
    text = g("diff", "HEAD~1..HEAD")
    out = []
    for s in summs:
        t = gate_diff_text(s, text)
        k = gate_diff(s, d, "HEAD~1", "HEAD")
        out.append((s, t.claims, k.claims))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--git", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    r = random.Random(a.seed)
    rep = {"python": sys.version.split()[0], "seed": a.seed, "cases": 0, "claims": 0,
           "decided": {"tests_added": 0, "symbol_added": 0}, "false": 0, "false_examples": [],
           "git_cases": 0, "door_disagreements": 0, "door_examples": [], "git_decided": 0, "git_false": 0}
    with tempfile.TemporaryDirectory() as root:
        made = 0
        while rep["cases"] < a.cases:
            made += 1
            res = one(r, made, root if rep["git_cases"] < a.git else None)
            if res is None:
                continue
            diff, out, git = res
            rep["cases"] += 1
            for summ, kind, verdict, why, decided, true in out:
                rep["claims"] += 1
                if decided:
                    rep["decided"][kind] += 1
                    if not true:
                        rep["false"] += 1
                        if len(rep["false_examples"]) < 6:
                            rep["false_examples"].append({"summary": summ, "why": why, "diff": diff})
            if git is not None:
                rep["git_cases"] += 1
                for s, t, k, truths in git:
                    for tc, kc, true in zip(t, k, truths):
                        tv, tw, kv, kw = tc.verdict, tc.why, kc.verdict, kc.why
                        if true is not None:
                            rep["git_decided"] += 1
                            rep["git_false"] += not true
                        if tw.endswith("(#101)") and (tv, tw) != (kv, kw):
                            rep["door_disagreements"] += 1
                            if len(rep["door_examples"]) < 4:
                                rep["door_examples"].append({"summary": s, "text": [tv, tw], "git": [kv, kw]})
    js = json.dumps(rep, indent=1)
    if a.out:
        Path(a.out).write_text(js + "\n")
    print(js)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
