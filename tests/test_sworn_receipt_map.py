"""The receipt map the README and .github/workflows/sworn.yml promise must be what the harness
mints, in that order, for the workflow's four commands. If either drifts, an author writing `rN`
before the run exists swears to the wrong bytes."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from styxx.sworn_harness import Harness

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "sworn.yml"

# What the documents promise (README table + workflow comment), by meaning.
PROMISED = {"commits.count": "r5", "diff.files_changed": "r11", "diff.insertions": "r12",
            "diff.deletions": "r13", "diff.patch": "r14", "diff.names": "r15", "ruff.exit_code": "r19",
            "pytest.argv": "r20", "pytest.stdout": "r21", "pytest.passed": "r24", "pytest.failed": "r25",
            "pytest.skipped": "r26", "pytest.xfailed": "r27", "pytest.errors": "r28"}


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, check=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "a.txt").write_text("one\n")
    _git(tmp_path, "add", "a.txt")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "a.txt").write_text("one\ntwo\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "change")
    return tmp_path, base, _git(tmp_path, "rev-parse", "HEAD")


def test_the_harness_mints_the_promised_ids_for_the_workflow_commands(repo):
    cwd, base, head = repo
    h = Harness(cwd / "m.json", turn="map", cwd=str(cwd))
    g = h.standard(base, head, ruff_argv=[sys.executable, "-m", "ruff", "--version"],
                   pytest_argv=[sys.executable, "-m", "pytest", "--version"])   # same shapes, fast
    c, d, r, p = g["commits"], g["diff"], g["ruff"], g["pytest"]
    minted = {"commits.count": c["count"], "diff.files_changed": d["files_changed"], "diff.insertions": d["insertions"],
              "diff.deletions": d["deletions"], "diff.patch": d["patch"], "diff.names": d["names"],
              "ruff.exit_code": r["exit_code"], "pytest.argv": p["argv"], "pytest.stdout": p["stdout"],
              "pytest.passed": p["passed"], "pytest.failed": p["failed"], "pytest.skipped": p["skipped"],
              "pytest.xfailed": p["xfailed"], "pytest.errors": p["errors"]}
    assert minted == PROMISED


def test_the_readme_table_and_the_workflow_comment_name_the_promised_ids():
    readme = README.read_text(encoding="utf-8")
    table = readme[readme.index("| receipt | holds |"):readme.index("A description that swears:")]
    for key, rid in PROMISED.items():
        if key in ("pytest.argv", "pytest.stdout") or key.startswith("diff.") or key.startswith("pytest.") \
                or key in ("commits.count", "ruff.exit_code"):
            assert re.search(r"`%s`" % rid, table), (key, rid)
    wf = WORKFLOW.read_text(encoding="utf-8")
    assert "r1-r6" in wf and "r7-r15" in wf and "r16-r19" in wf and "r20-r28" in wf
    # the example description in the README uses only promised ids
    example = readme[readme.index("A description that swears:"):readme.index("Policy, in one table")]
    for rid in set(re.findall(r'r="(r\d+)"', example)):
        assert rid in PROMISED.values(), rid
