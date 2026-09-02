"""styxx.referee: a refutation is ACCEPTED only when it is sworn, binds to its target's bytes, and
its re-derivation script is committed at the commit it names."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from styxx.referee import ACCEPTED, REJECTED, check, index
from styxx.sworn import to_sidecar
from styxx.sworn_harness import Harness

ROOT = Path(__file__).resolve().parent.parent


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, check=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "papers").mkdir()
    (tmp_path / "papers" / "RESULT_x.md").write_text("# RESULT — the gap is 0.31 — today\n\nbody\n")
    (tmp_path / "papers" / "rederive.py").write_text(
        "import json, sys\nprint(json.dumps({'adjusted': 0.117, 'raw': 0.3124}) if '--emit-json' in sys.argv else 'x')\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path, _git(tmp_path, "rev-parse", "HEAD")


def _refutation(cwd, commit, *, quote_target=True, cmd_path="papers/rederive.py"):
    h = Harness(cwd / "m.json", turn="ref", cwd=str(cwd))
    ids = h.exec([sys.executable, cmd_path, "--emit-json"])
    h.save()
    from styxx.sworn import Manifest
    m = Manifest.load(cwd / "m.json")
    doc = ("# REFUTATION\n\n"
           + ('Against <sworn r="path:papers/RESULT_x.md#L1" k="quote">the result that says `the gap is 0.31`</sworn>. ' if quote_target else "")
           + 'The harness ran <sworn r="%s" k="quote">`%s %s --emit-json`</sworn> and it printed '
             '<sworn r="%s" k="numeric">0.117</sworn> adjusted against <sworn r="%s" k="numeric">0.3124</sworn> raw.\n'
           % (ids["argv"], sys.executable, cmd_path, ids["/adjusted"], ids["/raw"])).encode()
    return to_sidecar(doc, "REFUTATION_x.md", commit, manifest=m)


def test_a_sworn_refutation_with_a_committed_script_and_a_quoted_target_is_accepted(repo):
    cwd, commit = repo
    r = check(_refutation(cwd, commit), cwd)
    assert r["status"] == ACCEPTED, r
    assert r["targets"] == ["papers/RESULT_x.md"] and r["scripts"] == ["papers/rederive.py"]


def test_no_quoted_target_is_rejected(repo):
    cwd, commit = repo
    r = check(_refutation(cwd, commit, quote_target=False), cwd)
    assert r["status"] == REJECTED and "no_target_quoted" in r["reasons"]


def test_an_uncommitted_script_is_rejected(repo):
    cwd, commit = repo
    (cwd / "papers" / "uncommitted.py").write_text((cwd / "papers" / "rederive.py").read_text())
    r = check(_refutation(cwd, commit, cmd_path="papers/uncommitted.py"), cwd)
    assert r["status"] == REJECTED and any(x.startswith("script_not_at_commit:papers/uncommitted.py") for x in r["reasons"])


def test_a_lie_in_the_refutation_is_rejected_by_the_verifier(repo):
    cwd, commit = repo
    side = _refutation(cwd, commit)
    side["document"]["text"] = side["document"]["text"].replace("0.117", "0.118", 1) if "text" in side["document"] else side["document"]["text"]
    from styxx.sworn import render
    raw = render(side).replace(b"0.117", b"0.118", 1)
    side2 = to_sidecar(raw, "REFUTATION_x.md", commit, manifest=None)
    side2["manifest"] = side["manifest"]
    r = check(side2, cwd)
    assert r["status"] == REJECTED and any(x.startswith("not_sworn_held") for x in r["reasons"])


def test_index_lists_targets(repo):
    cwd, commit = repo
    side = _refutation(cwd, commit)
    (cwd / "papers" / "REFUTATION_x.sworn.json").write_text(json.dumps(side))
    idx = index(cwd)
    assert list(idx) == ["papers/RESULT_x.md"] and idx["papers/RESULT_x.md"][0]["status"] == ACCEPTED


@pytest.mark.parametrize("sc", sorted(ROOT.glob("papers/**/REFUTATION_*.sworn.json")), ids=lambda p: p.name)
def test_every_committed_refutation_is_accepted_at_its_own_commit(sc):
    r = check(json.loads(sc.read_text(encoding="utf-8")), ROOT)
    assert r["status"] == ACCEPTED, r
