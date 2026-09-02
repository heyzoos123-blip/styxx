"""styxx.sworn_gate: the policy table over a sworn PR description, and the CLI that applies it."""
from __future__ import annotations

import json

from styxx.sworn import Manifest
from styxx.sworn_gate import FAIL, NEUTRAL, PASS, decide, main


def test_the_policy_table():
    held = {"HELD": 3, "FAILED": 0, "UNRESOLVED": 0, "MALFORMED": 0, "WITHHELD": 0}
    assert decide("SWORN-HELD", held) == PASS
    assert decide("SWORN-HELD", held, strict=True) == PASS
    assert decide("SWORN-FAILED", {**held, "FAILED": 1}) == FAIL
    assert decide("MALFORMED") == FAIL
    assert decide("UNSWORN", {**held, "HELD": 0}) == NEUTRAL
    assert decide("UNSWORN", strict=True) == FAIL
    # the verifier's SWORN-HELD tolerates an unresolved span; the gate does not pass it
    assert decide("SWORN-HELD", {**held, "UNRESOLVED": 1}) == NEUTRAL
    assert decide("SWORN-HELD", {**held, "UNRESOLVED": 1}, strict=True) == FAIL


def _manifest(tmp_path):
    """A manifest shaped like the workflow's, minted directly: r1 = passed count, r2 = exit code."""
    m = Manifest(harness="tests/test_sworn_gate.py", turn="pr-1")
    m.add("r1", b"7", "test_report", complete=True)
    m.add("r2", b"0", "harness_note", complete=True)
    m.write(tmp_path / "m.json")
    (tmp_path / "m.legend.json").write_text(json.dumps({"legend": {
        "r1": {"kind_of_source": "test_report", "what": "passed, extracted by the harness from: pytest"},
        "r2": {"kind_of_source": "harness_note", "what": "exit code of: pytest"}}}))
    return tmp_path / "m.json", {"passed": "r1", "exit_code": "r2"}


def test_cli_passes_a_held_description_and_writes_the_receipt(tmp_path, capsys):
    mp, ids = _manifest(tmp_path)
    body = tmp_path / "body.md"
    body.write_text('Suite: <sworn r="%s" k="numeric">7 passed</sworn>, exit <sworn r="%s" k="numeric">0</sworn>.\n'
                    % (ids["passed"], ids["exit_code"]))
    rc = main([str(body), "--manifest", str(mp), "--out", str(tmp_path / "gate.json")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "sworn-gate: PASS" in out and "legend" in out
    rec = json.loads((tmp_path / "gate.json").read_text())
    assert rec["gate"] == "PASS" and rec["receipt"]["document_verdict"] == "SWORN-HELD"


def test_cli_fails_a_lie(tmp_path, capsys):
    mp, ids = _manifest(tmp_path)
    body = tmp_path / "body.md"
    body.write_text('Suite: <sworn r="%s" k="numeric">8 passed</sworn>.\n' % ids["passed"])
    assert main([str(body), "--manifest", str(mp)]) == 1
    assert "sworn-gate: FAIL" in capsys.readouterr().out


def test_cli_fails_a_malformed_tag(tmp_path, capsys):
    mp, ids = _manifest(tmp_path)
    body = tmp_path / "body.md"
    body.write_text('Suite: <sworn r="%s" k="exec">7 passed</sworn>.\n' % ids["passed"])
    assert main([str(body), "--manifest", str(mp)]) == 1
    out = capsys.readouterr().out
    assert "sworn-gate: FAIL" in out and "MALFORMED" in out


def test_unsworn_is_neutral_unless_strict(tmp_path, capsys):
    mp, _ = _manifest(tmp_path)
    body = tmp_path / "body.md"
    body.write_text("Fixed the thing. All tests pass.\n")
    assert main([str(body), "--manifest", str(mp)]) == 0
    out = capsys.readouterr().out
    assert "sworn-gate: NEUTRAL" in out and "UNSWORN is not 'no failures'" in out
    assert main([str(body), "--manifest", str(mp), "--strict"]) == 1
    assert "sworn-gate: FAIL" in capsys.readouterr().out


def test_an_unresolved_receipt_is_neutral_not_pass_and_the_gate_never_mints_or_edits(tmp_path, capsys):
    mp, _ = _manifest(tmp_path)
    before = Manifest.load(mp).digest()
    body = tmp_path / "body.md"
    text = 'Suite: <sworn r="r99" k="numeric">7 passed</sworn>.\n'
    body.write_text(text)
    assert main([str(body), "--manifest", str(mp)]) == 0
    out = capsys.readouterr().out
    assert "sworn-gate: NEUTRAL" in out and "does not hold" in out
    assert main([str(body), "--manifest", str(mp), "--strict"]) == 1
    assert Manifest.load(mp).digest() == before
    assert body.read_text() == text
