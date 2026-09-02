"""styxx.sworn_preview: the author's mirror — same verdicts, working tree, no receipt."""
from __future__ import annotations

import hashlib
import json

from styxx.sworn_preview import WORKTREE, WorkTree, main, preview


def _tree(tmp_path):
    (tmp_path / "papers" / "arc").mkdir(parents=True)
    (tmp_path / "papers" / "arc" / "r.json").write_text(json.dumps({"acc": 0.9515, "n": 165}))
    (tmp_path / "papers" / "arc" / "PREREG_x.md").write_text("# prereg\n\nfrozen\n")
    return tmp_path


def test_a_path_receipt_resolves_from_disk_and_the_commit_is_worktree(tmp_path):
    root = _tree(tmp_path)
    doc = b'Held at <sworn r="path:papers/arc/r.json#/acc" k="numeric">0.9515</sworn>.\n'
    core = preview(doc, name="d.md", repo=root)
    assert core["document_verdict"] == "SWORN-HELD" and core["commit"] == WORKTREE
    lie = doc.replace(b"0.9515", b"0.9516")
    assert preview(lie, name="d.md", repo=root)["document_verdict"] == "SWORN-FAILED"


def test_a_missing_path_is_unresolved_never_an_accusation(tmp_path):
    root = _tree(tmp_path)
    doc = b'<sworn r="path:papers/arc/missing.json#/acc" k="numeric">0.9515</sworn>\n'
    core = preview(doc, name="d.md", repo=root)
    assert core["document_verdict"] == "SWORN-HELD"           # the verifier's rule: UNRESOLVED is not FAILED
    assert core["counts"]["UNRESOLVED"] == 1 and core["counts"]["HELD"] == 0


def test_a_prereg_receipt_resolves_by_content_from_disk(tmp_path):
    root = _tree(tmp_path)
    digest = hashlib.sha256((root / "papers" / "arc" / "PREREG_x.md").read_bytes()).hexdigest()
    doc = ('<sworn r="prereg:%s" k="quote">the prereg says `frozen`</sworn>\n' % digest).encode()
    assert preview(doc, name="d.md", repo=root)["document_verdict"] == "SWORN-HELD"


def test_the_worktree_never_reads_outside_the_root(tmp_path):
    root = _tree(tmp_path)
    (tmp_path.parent / "outside.json").write_text("{}")
    assert WorkTree(root).blob("../outside.json") == (None, "path_absent")


def test_cli_exit_codes_and_that_nothing_is_written(tmp_path, capsys):
    root = _tree(tmp_path)
    doc = root / "d.md"
    doc.write_bytes(b'<sworn r="path:papers/arc/r.json#/n" k="numeric">n=165</sworn>\n')
    before = sorted(p.name for p in root.rglob("*"))
    assert main([str(doc), "--repo", str(root)]) == 0
    out = capsys.readouterr().out
    assert "PREVIEW" in out and "no receipt" in out
    doc.write_bytes(b'<sworn r="path:papers/arc/r.json#/n" k="numeric">n=166</sworn>\n')
    assert main([str(doc), "--repo", str(root)]) == 1
    assert sorted(p.name for p in root.rglob("*")) == before
