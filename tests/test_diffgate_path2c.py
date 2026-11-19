"""PATH-2c, R-101c (papers/closed-model-frontier/PREREG_path2c_git_door_2026_11_19.md): #101 decided at the git
door only, by `ast` over the two commits' files. G-P1 (the issue) and G-P2 (the families), each read at both doors:
the git door matches the truth or keeps the overlay's verdict, the text door reads as on 45f351d1."""
import functools
import json
import os
import subprocess
from pathlib import Path

import pytest

from styxx.diffgate import gate_diff, gate_diff_text
from tests import _p2a_ref as R

FIXTURE = Path(__file__).parent / "fixtures" / "path2a_repros.json"
ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
WITHHELD = "withheld by PATH-2a (#101): "


def repo(tmp_path, base: dict, head: dict):
    def g(*a):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True, env=ENV)
    g("init", "-q")
    g("config", "user.email", "x@y")
    g("config", "user.name", "x")
    for p, text in base.items():
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / p).write_text(text)
    g("add", "-A")
    g("commit", "-qm", "base")
    for p in base:
        if p not in head:
            (tmp_path / p).unlink()
    for p, text in head.items():
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / p).write_text(text)
    g("add", "-A")
    g("commit", "-qm", "head")
    diff = subprocess.run(["git", "-C", str(tmp_path), "diff", "HEAD~1..HEAD"], check=True, capture_output=True,
                          text=True, env=ENV).stdout
    return diff


@functools.lru_cache(maxsize=None)
def main45():
    """45f351d1's reader: this file with R-101c's block and hook cut (R.lf does the cut), built as a module."""
    return R.module_from(R.lf(R.INSTRUMENT), "_diffgate_45f351d1")


def both(tmp_path, summary, base, head):
    """Both doors of this reader, each held to 45f351d1's on the same repository: the text door reads alike, and at
    the git door a claim reads alike or moves from the overlay's UNCHECKABLE to VERIFIED with a reason ending (#101)."""
    diff = repo(tmp_path, base, head)
    git, text = gate_diff(summary, tmp_path, "HEAD~1", "HEAD"), gate_diff_text(summary, diff)
    m = main45()
    assert reads(text) == reads(m.gate_diff_text(summary, diff))
    was = m.gate_diff(summary, tmp_path, "HEAD~1", "HEAD").claims
    assert len(was) == len(git.claims)
    for c, b in zip(git.claims, was):
        assert (c.kind, c.verdict, c.why) == (b.kind, b.verdict, b.why) or (
            b.verdict == "UNCHECKABLE" and WITHHELD in b.why and c.verdict == "VERIFIED" and c.why.endswith("(#101)"))
    return git, text


def reads(g):
    return [(c.kind, c.verdict, c.why) for c in g.claims]


# ---- G-P1 ------------------------------------------------------------------------------------------------------

ISSUE_BASE = {"src/retry.py": "def backoff(n):\n    return n * 2\n",
              "tests/test_retry.py": "def test_a():\n    assert True\n\n\ndef test_b():\n    assert True\n"}
ISSUE_HEAD = {"src/retry.py": "def backoff(n, jitter=0):\n    return n * 2\n",
              "tests/test_retry.py": ("def test_a():  # unchanged behaviour, comment added\n    assert True\n\n\n"
                                      "def test_b():  # unchanged behaviour, comment added\n    assert True\n")}


def test_the_issue_reproduction_is_the_fixture():
    case = next(c for c in json.loads(FIXTURE.read_text())["cases"] if c["id"] == "path2:101-the-issue")
    # the fixture's diff is this repository's diff, but for git's index lines and context header
    want = [x for x in case["diff"].split("\n") if not x.startswith(("diff ", "index "))]
    assert case["summary"] == "Adds function backoff with jitter. Added 2 tests."
    assert want[0] == "--- a/src/retry.py"


def test_g_p1_the_issue(tmp_path):
    summary = "Adds function backoff with jitter. Added 2 tests. Added 0 tests."
    git, text = both(tmp_path, summary, ISSUE_BASE, ISSUE_HEAD)
    sym, two, zero = git.claims
    assert (sym.kind, sym.verdict) == ("symbol_added", "UNCHECKABLE") and WITHHELD in sym.why
    assert (two.kind, two.verdict) == ("tests_added", "UNCHECKABLE") and WITHHELD in two.why
    assert (zero.verdict, zero.why) == ("VERIFIED", "the base and head files define 0 new test functions, the added "
                                                    "lines count 2, claim says 0 (#101)")
    assert git.verdict == "PASS"
    # the text door reads as on 45f351d1: all three withheld
    assert [c.verdict for c in text.claims] == ["UNCHECKABLE"] * 3
    assert all(WITHHELD in c.why for c in text.claims)
    assert reads(git)[:2] == reads(text)[:2]


# ---- G-P2 ------------------------------------------------------------------------------------------------------

def test_a_new_test_beside_a_changed_one(tmp_path):
    git, text = both(tmp_path, "Added 1 test. Added 2 tests.",
                     {"tests/test_x.py": "def test_a():\n    assert True\n"},
                     {"tests/test_x.py": "def test_a(tmp_path):\n    assert True\n\n\ndef test_new():\n    pass\n"})
    one, two = git.claims
    assert (one.verdict, one.why) == ("VERIFIED", "the base and head files define 1 new test functions, the added "
                                                  "lines count 2, claim says 1 (#101)")
    assert two.verdict == "UNCHECKABLE" and WITHHELD in two.why
    assert [c.verdict for c in text.claims] == ["UNCHECKABLE", "UNCHECKABLE"]


def test_a_test_moved_to_another_file_counts_as_added(tmp_path):
    git, _text = both(tmp_path, "Added 1 test. Added 0 tests.",
                      {"tests/test_a.py": "def test_x():\n    assert True\n", "tests/test_b.py": "y = 1\n"},
                      {"tests/test_a.py": "z = 1\n",
                       "tests/test_b.py": "y = 1\ndef test_x():\n    assert True\n"})
    one, zero = git.claims
    assert one.verdict == "VERIFIED" and one.why.endswith("(#101)")
    assert zero.verdict == "UNCHECKABLE"


def test_a_test_moved_from_a_class_to_module_level_counts_as_added(tmp_path):
    git, _text = both(tmp_path, "Added 1 test.",
                      {"tests/test_x.py": "class TestA:\n    def test_x(self):\n        pass\n"},
                      {"tests/test_x.py": "class TestA:\n    pass\n\n\ndef test_x():\n    pass\n"})
    assert git.claims[0].verdict == "VERIFIED" and git.claims[0].why.endswith("(#101)")


def test_a_deleted_test_and_a_new_one_of_its_name_add_none(tmp_path):
    git, _text = both(tmp_path, "Added 0 tests. Added 1 test.",
                      {"tests/test_x.py": "def test_x():\n    assert 1\n\n\nX = 2\n"},
                      {"tests/test_x.py": "X = 2\n\n\ndef test_x():\n    assert 2\n"})
    zero, one = git.claims
    assert zero.verdict == "VERIFIED" and zero.why.endswith("claim says 0 (#101)")
    assert one.verdict == "UNCHECKABLE"


def test_a_renamed_class_above_unchanged_tests_is_decided_by_the_truth(tmp_path):
    body = "".join(f"    def test_{i}(self):\n        pass\n\n" for i in range(8))
    git, text = both(tmp_path, "Added 0 tests. Added 1 test. Added 9 tests.",
                     {"tests/test_x.py": "class TestA:\n    def test_k(self):\n        pass\n\n" + body},
                     {"tests/test_x.py": "class TestB:\n    def test_k(self, x):\n        pass\n\n" + body})
    verdicts = [(c.verdict, c.why.endswith("(#101)")) for c in git.claims]
    # the truth: the class's nine tests all have a new qualified name, so 9 are added; neither 0 nor 1 is decided
    assert verdicts[0][0] == "UNCHECKABLE" and verdicts[1][0] == "UNCHECKABLE"
    assert git.claims[2].verdict == "CONTRADICTED"      # main's own verdict (9 > the 1 it counts) stands
    assert all(c.verdict != "VERIFIED" for c in text.claims)


def test_a_name_defined_twice_in_one_scope_is_decided_by_the_truth(tmp_path):
    git, text = both(tmp_path, "Added 0 tests. Added 1 test. Added 2 tests.",
                     {"tests/test_x.py": "def test_a():\n    pass\n\n\ndef test_a():\n    pass\n"},
                     {"tests/test_x.py": ("def test_a(x):\n    pass\n\n\ndef test_a():\n    pass\n\n\n"
                                          "def test_c():\n    pass\n")})
    zero, one, two = git.claims
    assert (one.verdict, one.why) == ("VERIFIED", "the base and head files define 1 new test functions, the added "
                                                  "lines count 2, claim says 1 (#101)")   # test_a was there already
    assert two.verdict == "UNCHECKABLE" and WITHHELD in two.why
    assert reads(git)[0] == reads(text)[0] and zero.verdict == "CONTRADICTED"   # main's own, not withheld


def test_a_claim_the_overlay_does_not_withhold_stays_as_on_main(tmp_path):
    # the diff shows the old test_b as added; main reads "Added 0 tests." CONTRADICTED and the overlay keeps it, so
    # by section 4 R-101c cannot move it, though the truth is 0
    git, text = both(tmp_path, "Added 0 tests. Added 1 test.",
                     {"tests/test_x.py": "def test_a():\n    pass\n\n\ndef test_b():\n    pass\n"},
                     {"tests/test_x.py": ("def test_a(x):\n    pass\n\n\ndef test_b():\n    pass\n\n\n"
                                          "def test_b():\n    pass\n")})
    assert reads(git) == reads(text)
    assert git.claims[0].verdict == "CONTRADICTED" and git.claims[1].verdict == "UNCHECKABLE"


def test_a_file_that_does_not_parse_decides_nothing(tmp_path):
    for side in ("base", "head"):
        d = tmp_path / side
        d.mkdir()
        broken = "def test_a(:\n"
        base = {"tests/test_x.py": broken if side == "base" else "def test_a():\n    pass\n"}
        head = {"tests/test_x.py": "def test_a(x):\n    pass\n" if side == "base" else broken + "def test_a(x):\n"}
        git, text = both(d, "Added 0 tests.", base, head)
        assert reads(git) == reads(text)
        assert all(c.why.endswith("(#101)") is False for c in git.claims)


def test_a_def_test_in_markdown_decides_nothing(tmp_path):
    git, text = both(tmp_path, "Added 1 test.",
                     {"tests/test_x.py": "def test_a():\n    pass\n", "notes.md": "x\n"},
                     {"tests/test_x.py": "def test_a(x):\n    pass\n", "notes.md": "x\ndef test_b():\n"})
    assert reads(git) == reads(text)


def test_a_type_change_decides_nothing(tmp_path):
    diff = repo(tmp_path, {"tests/test_x.py": "def test_a():\n    pass\n", "tests/test_y.py": "Y = 1\n"},
                {"tests/test_x.py": "def test_a(x):\n    pass\n", "tests/test_y.py": "Y = 1\n"})
    (tmp_path / "tests/test_y.py").unlink()
    os.symlink("test_x.py", tmp_path / "tests/test_y.py")
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qam", "type"], check=True, capture_output=True, env=ENV)
    git = gate_diff("Added 0 tests.", tmp_path, "HEAD~2", "HEAD")
    assert git.claims[0].verdict == "UNCHECKABLE" and WITHHELD in git.claims[0].why
    assert diff


def test_a_name_added_as_a_class_where_the_claim_says_function_is_not_decided(tmp_path):
    git, _text = both(tmp_path, "Adds function backoff.",
                      {"src/a.py": "def backoff():\n    pass\n"},
                      {"src/a.py": "def backoff(x):\n    pass\n\n\nclass Box:\n    class backoff:\n        pass\n"})
    assert git.claims[0].verdict == "UNCHECKABLE" and WITHHELD in git.claims[0].why
    git2 = gate_diff("Adds class backoff.", tmp_path, "HEAD~1", "HEAD")
    assert git2.claims[0].verdict == "VERIFIED"
    assert git2.claims[0].why == "the head files define class 'backoff' where the base files do not (#101)"


def test_a_symbol_added_in_another_class_is_verified(tmp_path):
    git, _text = both(tmp_path, "Adds method close.",
                      {"src/a.py": "class A:\n    def close(self):\n        pass\n"},
                      {"src/a.py": "class A:\n    def close(self, x):\n        pass\n\n\nclass B:\n"
                                   "    def close(self):\n        pass\n"})
    assert git.claims[0].verdict == "VERIFIED"


def test_a_symbol_changed_in_place_stays_withheld(tmp_path):
    git, text = both(tmp_path, "Adds method close.",
                     {"src/a.py": "class A:\n    def close(self):\n        pass\n"},
                     {"src/a.py": "class A:\n    def close(self, x):\n        pass\n"})
    assert reads(git) == reads(text)


@pytest.mark.parametrize("noun", ["case", "cases", "suites"])
def test_a_count_noun_other_than_functions_is_not_decided(tmp_path, noun):
    git, text = both(tmp_path, f"Added 1 test {noun}.",
                     {"tests/test_x.py": "def test_a():\n    pass\n"},
                     {"tests/test_x.py": "def test_a(x):\n    pass\n\n\ndef test_b():\n    pass\n"})
    assert all(not c.why.endswith("(#101)") for c in git.claims)


def test_no_contradicted_is_added_and_strict_reads_the_moved_claims(tmp_path):
    summary = "Added 0 tests."
    diff = repo(tmp_path, ISSUE_BASE, ISSUE_HEAD)
    assert gate_diff(summary, tmp_path, "HEAD~1", "HEAD", strict=True).verdict == "PASS"
    assert gate_diff_text(summary, diff, strict=True).verdict == "FAIL"
