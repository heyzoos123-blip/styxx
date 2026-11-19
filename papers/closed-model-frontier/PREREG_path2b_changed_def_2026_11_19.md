# PREREG — PATH-2b: a changed `def` is decided where the whole of its file up to it is in the diff (#101)

Fathom Lab · 2026-11-19 · **DRAFT, unsigned.** Written by the lead before any code of the repair, on branch
`papers/path2b-changed-def-prereg` at `main` `45f351d1`, where `styxx/diffgate.py` hashes to
`80d0e79e2639eb8c…` and `web/gate/diffgate.js` to `ecaf5ccb6caa7e51…` (sha256 of the committed bytes). Amends
`PREREG_path2_resolution_2026_09_17.md` (on the branch of #161, `fix/diffgate-path-resolution`, commit `97e84502`),
for #101 only, and acts on the open goal `AMENDMENT_path2_withholding_2026_10_06.md` states: "Repair remains the
open goal." #97 and #121 are not in this freeze. The operator's choice of scope (section 8) and the Signature are
TO-FILL at the signing commit.

## 1. Where #101 stands on `45f351d1`

- Main's reader counts `def test_` and `def NAME` in added lines only, so a changed definition reads as an added one.
- The PATH-2a overlay (#187) withholds, as UNCHECKABLE, a `tests_added` claim whose count lies in
  `[got − chg, got]` where `chg ≥ 1` tests the added lines define are also defined in the removed lines
  (`_p2a_tests`), and a VERIFIED `symbol_added` whose name a removed line defines (`_p2a_symbol`). On the issue's
  diff both claims read UNCHECKABLE, gate PASS; "Added 0 tests.", true there, reads CONTRADICTED withheld.
- #161's R-101 ended abstain-only. Its pass eight (Y-5) withdrew the row "`net = n` → VERIFIED", after two probes
  read "Added 1 test." VERIFIED where main read CONTRADICTED and the truth was 0: a `def test_` inside a string
  opened in lines the diff does not show, and one in a file that is not Python. Pass fifteen confirmed the #101
  part decided no verdict of its own (`NOTE_path2_fifteenth_pass_2026_09_29.md`).

So a repair adds something only where it brings back a decided verdict the overlay withholds, and every such
verdict must be the truth. That is the whole of this round.

## 2. Truth

For a `+++` section of a `.py` or `.pyi` file, the tests a diff adds are the qualified names (the file's path, the
enclosing `class` names, the function's name) of functions whose name begins `test_` that CPython's `ast`, on the
head file, defines and, on the base file, does not. A test deleted and a new one of the same qualified name added
counts as none added; a test moved to another file or another class counts as added. A symbol is added when its
qualified name is defined at head and not at base. The scorer reads truth from the base and head files the
differential builds, never from the diff.

## 3. The repair, R-101b

R-101b changes the overlay's `_p2a_tests` and `_p2a_symbol` in both ports, and nothing in main's reader. Where a
claim the overlay withholds meets every condition of K below, the overlay decides it; otherwise its decision on
`45f351d1` stands byte for byte.

**K, the whole-prefix condition.** For every `+++` section that holds a `def test_` line (for `symbol_added`, a line
defining NAME) on either side:

- K1. The section's path ends in `.py` or `.pyi` (read as `_python_source_lines` reads it), and it is neither a new
  nor a deleted file.
- K2. Its hunks run without a gap from line 1 of both sides through the last such line: the earliest hunk header
  reads `@@ -1,a +1,b @@`, each next hunk begins where the one before ends on both sides, and each hunk holds exactly
  the counts its header declares. A section whose hunks do not parse so fails K.
- K3. The triple-quote parity of every such line, counted from line 1 over that side's context and changed lines,
  is even, and so is the parity at the end of the last hunk on each side.
- K4. Every such line is ASCII, holds no code point either port reads apart (`_SEAM_WS`, `_P2A_DIVERGENT`), and the
  name in it is ASCII; no #205 seam, no #179 twice, no Y-6 fold doubt, and no B-1 redefinition in a context line.
- K5. Both ports' views of the section are alike (the overlay's `alike`), and the `---`/`+++` headers are ones both
  ports cut alike.

**Within K, the decision.** Per section and per qualified name, `chg = Σ min(added, removed)` (one to one), where the
qualified name is read from the indentation of the visible prefix: a `def` is in the innermost `class` line before
it at a smaller indentation. `net = got − chg`.

| claim | overlay on `45f351d1` | R-101b within K |
|---|---|---|
| `tests_added`, `n = net`, function noun | UNCHECKABLE (withheld) | VERIFIED, `diff adds {net} test functions and changes {chg}, claim says {n} (#101)` |
| `tests_added`, `net < n ≤ got` | UNCHECKABLE | unchanged |
| `tests_added`, `n < net` or `n > got` | main's CONTRADICTED stands | unchanged |
| `symbol_added`, some section adds NAME more times than it removes it, at one qualified name | UNCHECKABLE (withheld) | VERIFIED, `added lines define {kind} {NAME!r} where the removed lines of the same file do not (#101)` |
| `symbol_added`, every added NAME paired | UNCHECKABLE | unchanged |

No CONTRADICTED is added. A count noun other than functions (#110) is not decided.

**The port.** `web/gate/diffgate.js` carries R-101b with the same reasons byte for byte; the bookmarklet is rebuilt
with `build_bookmarklet.py`; new pairs go in `web/gate/differential/path2b_pairs.json`.

## 4. What cannot move, by construction

- Any claim of a kind other than `tests_added` and `symbol_added`; any claim the overlay does not withhold on
  `45f351d1`; any claim on a diff where some relevant section fails K.
- Which sentences are read and which claims they yield.
- A move is only UNCHECKABLE → VERIFIED, and only with a reason ending `(#101)`.

## 5. Gates

### Unit gates. Blocking; a failure blocks the corpus run.

- **G-P1 (the reproductions).** The issue's diff, whose hunks do not begin at line 1, reads as on `45f351d1`:
  both claims UNCHECKABLE, gate PASS. The same change written as a diff of whole files (`git diff -U100000`) reads
  "Added 0 tests." VERIFIED and "Added 2 tests." UNCHECKABLE, with the reasons of section 3, on both doors and
  both ports.
- **G-P2 (the probes #161 found).** Each of these leaves the overlay's verdict as it was: pass eight's string opened
  in a line the diff does not show, and its `def test_` in a Markdown file; a removed SQL comment printed `--- x`;
  a byte order mark on line 1 and elsewhere; a lone CR, a backslash continuation, an NBSP, VT, FF or U+2028 in an
  indent; an `async def` beside a changed sync test; a name with a code point past ASCII; case-fold twin paths.
  Each of these is decided within K and matches truth: a new test beside a changed one ("Added 1 test."); a test
  moved to another file; a test moved from a class to module level; a deleted test and a new one of its name.
- **G-P3 (the doors agree).** For each G-P1 and G-P2 diff on a two-commit repository, `gate_diff` and
  `gate_diff_text` over `git diff` give the same claims, verdicts and reasons.
- **G-P4 (the differential).** `check_pairs.js`: 0 disagreements on every pinned pair. A generated differential of
  at least 30,000 cases (base and head files built from the probe families above and random edits) on CPython
  3.9 to 3.14 and Node: 0 Python/JavaScript disagreements beyond those on `45f351d1`, and 0 decided verdicts
  R-101b adds that differ from truth.
- **G-P5 (suite, demo, bookmarklet).** Every diffgate test module and every test importing `styxx.diffgate` or
  reading `web/gate` is green; `--demo` prints the same bytes; `build_bookmarklet.py --check` matches.

### Corpus gates, on the EXTERNAL-1 shelf (`external1_shelf.sqlite`), baseline `45f351d1`

- **G-C1.** The ordered claims of every eligible PR are identical. Blocking.
- **G-C2.** Every claim that moves is `tests_added` or `symbol_added`, from UNCHECKABLE to VERIFIED, with a reason
  ending `(#101)`. Blocking.
- **G-C3.** Every moved claim is read by hand against the PR's base and head files and is true. Blocking.
- **G-C4 (report only).** Moves by kind; how many withheld #101 claims fail which part of K, so the yield is seen.

## 6. The gates block

```gates
{"gates": {"G_P1": {"power_basis": "the reproduction gate of PREREG_path2's G-P1, restated for R-101b: a pass or fail of fixed tests, so no sample and no power",
                    "metric": "result.unit.p1_reproductions_pass", "op": ">=", "value": 1,
                    "metric_means": "1 if every G-P1 test fails on 45f351d1 or pins its unchanged verdict there, and passes after"},
           "G_P2": {"power_basis": "one probe per defect family #161's fifteen passes found against its #101 part (NOTE_path2_third to fifteenth pass); a fixed list, no sample",
                    "metric": "result.unit.p2_probes_pass", "op": ">=", "value": 1,
                    "metric_means": "1 if every G-P2 probe reads as section 5 says on both ports and both doors"},
           "G_P3": {"power_basis": "PREREG_path2's G-P3: any door disagreement on a fixed diff blocks, so the bar is zero",
                    "metric": "result.unit.p3_door_disagreements", "op": "<=", "value": 0,
                    "metric_means": "G-P1 and G-P2 diffs on which gate_diff and gate_diff_text differ in a claim, verdict or reason"},
           "G_P4": {"power_basis": "the merge bar of section 7 allows no false decided verdict and no new port disagreement, so the bar is zero; 30,000 cases is the size #161's pass fifteen said was owed (NOTE_path2_fifteenth_pass, G)",
                    "metric": "result.unit.p4_wrong_or_split", "op": "<=", "value": 0,
                    "metric_means": "generated cases where an R-101b decision differs from truth, plus new Python/JavaScript disagreements"},
           "G_P5": {"power_basis": "PREREG_path2's G-P5, unchanged",
                    "metric": "result.unit.p5_suite_green", "op": ">=", "value": 1,
                    "metric_means": "1 if the suites, the demo bytes and the bookmarklet check all pass"},
           "G_C1": {"power_basis": "PREREG_path2's G-C1: extraction reads the summary alone and R-101b does not touch it, so any difference is a defect",
                    "metric": "result.corpus.c1_claim_lists_differ", "op": "<=", "value": 0,
                    "metric_means": "eligible PRs whose ordered claim list differs between baseline and repair"},
           "G_C2": {"power_basis": "section 4: R-101b can move only UNCHECKABLE to VERIFIED on two kinds with a (#101) reason, so any other move is a defect",
                    "metric": "result.corpus.c2_moves_outside_rule", "op": "<=", "value": 0,
                    "metric_means": "moved claims that are not tests_added or symbol_added going UNCHECKABLE to VERIFIED with a reason ending (#101)"},
           "G_C3": {"power_basis": "section 7: a false restored VERIFIED is worse than main with the overlay, so the bar is zero",
                    "metric": "result.corpus.c3_moved_and_false", "op": "<=", "value": 0,
                    "metric_means": "moved claims the hand reading of base and head files finds false"}},
 "outcomes": [{"when": {"G_P1": false}, "verdict": "BLOCKED__g_p1_failed__no_corpus_run"},
              {"when": {"G_P2": false}, "verdict": "BLOCKED__g_p2_failed__no_corpus_run"},
              {"when": {"G_P3": false}, "verdict": "BLOCKED__g_p3_failed__no_corpus_run"},
              {"when": {"G_P4": false}, "verdict": "BLOCKED__g_p4_failed__no_corpus_run"},
              {"when": {"G_P5": false}, "verdict": "BLOCKED__g_p5_failed__no_corpus_run"},
              {"when": {"G_C1": false}, "verdict": "SECOND_FREEZE__g_c1_a_record_moved_unexplained"},
              {"when": {"G_C2": false}, "verdict": "SECOND_FREEZE__g_c2_a_record_moved_unexplained"},
              {"when": {"G_C3": false}, "verdict": "NOT_LANDED__a_restored_verdict_is_false"},
              {"when": {"G_P1": true, "G_P2": true, "G_P3": true, "G_P4": true, "G_P5": true,
                        "G_C1": true, "G_C2": true, "G_C3": true}, "verdict": "LANDS__r101b_decides_within_k"}],
 "smoke_verdict": "INVALID__smoke_plumbing_only"}
```

Rows are read in order and the earliest whose `when` holds gives the verdict.

## 7. The merge bar

No claim reads worse than on `45f351d1` with the overlay, on any door, port or runtime, judged against truth
(section 2); no new Python/JavaScript disagreement; the scorer and the tests cannot admit a planted defect. A
restored VERIFIED that is false is worse.

## 8. The operator's choice (TO-FILL)

- **Option A, this freeze as written.** The diff alone decides, under K. Provable, both doors alike, small yield:
  a default diff with three lines of context meets K2 only for a short file, or where the changes run from its top.
- **Option B, A and the git door reads whole files.** `gate_diff` reads the base and head blobs and decides by
  `ast`, so it decides most withheld #101 claims; `gate_diff_text` keeps option A. This breaks G-P3, which the
  operator would amend to "the doors agree wherever the text door decides".

## 9. What is not claimed

No precision figure; the path accusation stays withheld; #97 and #121 stay open; nothing restores a licence #161
withdrew; no committed receipt, PREREG, RESULT or NOTE is edited.

## 10. What failure means

A failure of G-P1 to G-P5 blocks the corpus run, and the overlay stays as it is. A failure of G-C1 or G-C2 means a
record moved that R-101b does not explain: the branch does not land, and a further freeze follows. A failure of G-C3
means a restored verdict is false: the branch does not land.

## Signature

TO-FILL at the signing commit: the operator's word, quoted, with its date, and the option of section 8.
