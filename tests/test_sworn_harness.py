"""styxx.sworn_harness: harness-minted receipts for a coding agent's report.

The point under test is invariant 2 in the coding setting — the AUTHOR never extracts. Every
scalar the harness mints comes from its fixed extractor table; every kind it mints is external;
a document that swears to those receipts verifies with no tree at all."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from styxx.sworn import SOURCE_KINDS_AUTHOR, SOURCE_KINDS_EXTERNAL, Manifest, verify
from styxx.sworn_harness import (Harness, extract_count, extract_pytest, extract_shortstat, main)


def test_extractors_read_only_the_tool_summary_shapes():
    assert extract_pytest(b"....\n12 passed, 2 skipped in 0.3s\n", b"") == {"passed": 12, "failed": 0, "skipped": 2}
    assert extract_pytest(b"3 failed, 9 passed, 1 xfailed, 1 error in 1s\n", b"") == \
        {"passed": 9, "failed": 3, "xfailed": 1, "errors": 1}
    assert extract_pytest(b"", b"") == {"passed": 0, "failed": 0}
    assert extract_shortstat(b" 3 files changed, 10 insertions(+), 2 deletions(-)\n", b"") == \
        {"files_changed": 3, "insertions": 10, "deletions": 2}
    assert extract_shortstat(b" 1 file changed, 1 deletion(-)\n", b"") == \
        {"files_changed": 1, "insertions": 0, "deletions": 1}
    assert extract_shortstat(b"", b"") == {"files_changed": 0, "insertions": 0, "deletions": 0}
    assert extract_count(b"41\n", b"") == {"count": 41}
    assert extract_count(b"fatal: bad revision\n", b"") == {}


def test_exec_mints_stdout_stderr_and_exit_code_as_external_kinds(tmp_path):
    h = Harness(tmp_path / "m.json", turn="t1", cwd=str(tmp_path))
    ids = h.exec([sys.executable, "-c", "import sys; print('hello'); sys.stderr.write('warn'); sys.exit(3)"])
    h.save()
    m = Manifest.load(tmp_path / "m.json")
    assert m.intact()
    assert m.receipts[ids["stdout"]]["kind_of_source"] == "tool_stdout"
    assert m.receipts[ids["stderr"]]["kind_of_source"] == "tool_stderr"
    assert m.receipts[ids["exit_code"]]["kind_of_source"] == "harness_note"
    assert {e["kind_of_source"] for e in m.receipts.values()} <= SOURCE_KINDS_EXTERNAL
    assert not ({e["kind_of_source"] for e in m.receipts.values()} & SOURCE_KINDS_AUTHOR)
    legend = json.loads((tmp_path / "m.legend.json").read_text())
    assert set(legend["legend"]) == set(m.receipts)
    # the receipts are the bytes the tool wrote
    import base64
    assert base64.b64decode(m.receipts[ids["stdout"]]["bytes"]) == b"hello\n"
    assert base64.b64decode(m.receipts[ids["exit_code"]]["bytes"]) == b"3"


def test_an_unknown_command_yields_no_extracted_scalars(tmp_path):
    h = Harness(tmp_path / "m.json", turn="t1", cwd=str(tmp_path))
    ids = h.exec([sys.executable, "-c", "print('3 files changed, 10 insertions(+)')"])
    assert set(ids) == {"stdout", "stderr", "exit_code"}, "the author cannot make the harness extract"


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
    (tmp_path / "b.txt").write_text("b\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "change")
    (tmp_path / "b.txt").write_text("bb\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "change 2")
    return tmp_path, base, _git(tmp_path, "rev-parse", "HEAD")


def test_diff_and_commits_mint_harness_extracted_scalars(repo):
    cwd, base, head = repo
    h = Harness(cwd / "m.json", turn="t2", cwd=str(cwd))
    d = h.diff(base, head)
    c = h.commits(base, head)
    h.save()
    m = Manifest.load(cwd / "m.json")
    import base64
    val = lambda rid: base64.b64decode(m.receipts[rid]["bytes"])  # noqa: E731
    assert val(d["files_changed"]) == b"2" and val(d["insertions"]) == b"2" and val(d["deletions"]) == b"0"
    assert val(d["names"]) == b"a.txt\nb.txt\n"
    import hashlib
    patch = subprocess.run(["git", "diff", base, head], cwd=str(cwd), capture_output=True, check=True).stdout
    assert "bytes" not in m.receipts[d["patch"]], "the patch rides as a digest only"
    assert m.receipts[d["patch"]]["sha256"] == hashlib.sha256(patch).hexdigest()
    assert val(c["count"]) == b"2"
    assert len(val(c["list"]).split()) == 2
    assert m.receipts[d["files_changed"]]["kind_of_source"] == "harness_note"


def test_a_report_sworn_to_harness_receipts_verifies_without_a_tree(repo):
    cwd, base, head = repo
    h = Harness(cwd / "m.json", turn="t3", cwd=str(cwd))
    d = h.diff(base, head)
    c = h.commits(base, head)
    e = h.exec([sys.executable, "-c", "print('12 passed in 0.1s')"])
    h.save()
    m = Manifest.load(cwd / "m.json")
    doc = ("# report\n\nThis change touched <sworn r=\"%s\" k=\"numeric\">2 files</sworn> across "
           "<sworn r=\"%s\" k=\"numeric\">2 commits</sworn>, adding "
           "<sworn r=\"%s\" k=\"numeric\">2 lines</sworn>; the run exited "
           "<sworn r=\"%s\" k=\"numeric\">0</sworn> and the changed files were "
           "<sworn r=\"%s\" k=\"quote\">the changed files included `b.txt`</sworn>.\n"
           % (d["files_changed"], c["count"], d["insertions"], e["exit_code"], d["names"])).encode()
    core = verify(doc, name="report.md", manifest=m)
    assert core["document_verdict"] == "SWORN-HELD", core["spans"]
    # a lie against the same receipts fails; the author cannot re-extract their way out
    lie = doc.replace(b">2 files<", b">3 files<")
    core = verify(lie, name="report.md", manifest=m)
    assert core["document_verdict"] == "SWORN-FAILED"
    assert [s["verdict"] for s in core["spans"]].count("FAILED") == 1


def test_cli_new_exec_diff_commits_roundtrip(repo, capsys):
    cwd, base, head = repo
    mp = cwd / "turn.json"
    assert main([str(mp), "--cwd", str(cwd), "new", "--turn", "t4"]) == 0
    assert main([str(mp), "--cwd", str(cwd), "exec", "--", sys.executable, "-c", "print('ok')"]) == 0
    assert main([str(mp), "--cwd", str(cwd), "diff", base, head]) == 0
    assert main([str(mp), "--cwd", str(cwd), "commits", base, head]) == 0
    m = Manifest.load(mp)
    assert m.intact() and len(m.receipts) == 3 + 8 + 5
    with pytest.raises(SystemExit):
        main([str(mp), "--cwd", str(cwd), "new", "--turn", "again"])
