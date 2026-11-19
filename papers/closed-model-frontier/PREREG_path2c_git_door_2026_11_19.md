# PREREG — PATH-2c: #101 decided at the git door only, by `ast` over the two commits' files

Fathom Lab · 2026-11-19 · **DRAFT, unsigned.** Written by the lead before any code of the repair, on branch
`papers/path2c-git-door-prereg` at `164799b6`. The code baseline is `main` `45f351d1`, where `styxx/diffgate.py`
hashes to `80d0e79e2639eb8c…` and `web/gate/diffgate.js` to `ecaf5ccb6caa7e51…` (sha256 of the committed bytes); the
R-101b code of `0ed76184` is not carried forward. Amends `PREREG_path2b_changed_def_2026_11_19.md` (sealed at
`92d61aab`) for the rest of #101. The Signature is TO-FILL at the signing commit.

## 1. What was seen before this was written

`NOTE_path2b_g_p4_2026_11_19.md`, and its six reports in `path2b_g_p4_runs/`. R-101b as frozen, run on 30,000
generated cases on each of CPython 3.9.25 to 3.14.6 (seed 1, identical on all six):

- the text door, reading the diff alone under K, decided 2,519 verdicts and 174 were false (all `tests_added`): 136
  where a line opening a scope changed (a renamed `class`, a test moved out of a class) and tests the diff shows as
  context, or does not show, changed qualified name with it; 38 where a test name is defined twice in one scope, in
  the lines shown or below them;
- the git door, reading both commits' files by `ast`, decided 153 verdicts on 300 cases, none false.

Also seen, exploratory and not a gate (seed 2, 6,000 cases): the text door with scopes required alike on both sides,
7 false; with that and `net = 0` only, 1 false, a class renamed in another Python file of the same diff. A diff that
stops before the end of a file cannot show a set of qualified names, so this freeze does not decide from a diff.

## 2. Truth

PATH-2b's section 2, unchanged, with the kind read for `symbol_added`. The tests a change adds are the qualified
names (path, enclosing `class` names, name) of functions named `test_…` that CPython's `ast` defines in the head
file and not in the base file, over the `.py` and `.pyi` files. A `symbol_added` claim of kind `function` or `method`
is true when some qualified name ending in NAME is a `def` or `async def` at head and is defined by no kind at base;
of kind `class`, the same with `class` at head.

## 3. The repair, R-101c

The text door (`gate_diff_text`), the GitHub Action (which reads a diff through it), the port
(`web/gate/diffgate.js`) and the bookmarklet keep `45f351d1`'s verdicts and reasons byte for byte. The PATH-2a
overlay's block is not edited. R-101c runs in `gate_diff` alone, after the overlay, outside its block.

**Which claims.** A `tests_added` or `symbol_added` claim the overlay withheld for #101 with the phrase `tests`,
`split`, `redefined`, `symbol` or `again`. A claim withheld for reading the summary (`extract`), or for the overlay's
own failure (`unparsed`, `unreproduced`, `error`, `malformed`), is not decided.

**What it reads.** `git diff --name-status -z --no-renames base..head`. Every `.py` or `.pyi` path in it has status
A, D or M, or nothing is decided; for each, the base blob (D, M) and the head blob (A, M) from `git cat-file blob`,
parsed as bytes by the running CPython's `ast.parse`. If any of them does not parse (SyntaxError, ValueError,
RecursionError, MemoryError, OverflowError), nothing is decided. A rename reads as a deletion and an addition, so a
moved test counts as added, as the truth says.

**The guard.** Every `+++` section whose added lines main's count reads (its `def test_` regex; for `symbol_added`,
its definition pattern for NAME) lies in a `.py` or `.pyi` path, or the claim is not decided: main counted a line the
truth does not read.

**The decision.**

| claim | overlay on `45f351d1` | R-101c at the git door |
|---|---|---|
| `tests_added`, noun none or `function(s)`, `n` = the truth's count, `n ≤ got` | UNCHECKABLE (withheld) | VERIFIED, `the base and head files define {n} new test functions, the added lines count {got}, claim says {n} (#101)` |
| `tests_added`, `n` ≠ the truth's count | UNCHECKABLE | unchanged |
| `symbol_added`, NAME added of the claim's kind (section 2) | UNCHECKABLE (withheld) | VERIFIED, `the head files define {kind} {NAME!r} where the base files do not (#101)` |
| `symbol_added`, otherwise | UNCHECKABLE | unchanged |

No CONTRADICTED is added at either door. A count noun other than functions (#110) is not decided. `got` is read from
main's reason (`diff adds {got} test functions, claim says {n}`).

## 4. What cannot move, by construction

- Anything at the text door, in the Action, the port or the bookmarklet.
- At the git door: any claim of another kind, any claim the overlay does not withhold, any claim on a commit pair
  where section 3's reading or guard fails. A move is only UNCHECKABLE → VERIFIED, with a reason ending `(#101)`.
- Which sentences are read and which claims they yield.

## 5. Gates

### Unit gates. Blocking; a failure blocks the rest.

- **G-P1 (the issue).** The reproduction `path2:101-the-issue`, built as a two-commit repository: at the git door
  "Added 0 tests." VERIFIED, "Added 2 tests." and "Adds function backoff with jitter." UNCHECKABLE as on
  `45f351d1`; at the text door, all three as on `45f351d1`.
- **G-P2 (the families).** At the git door, each matches the truth or stays as on `45f351d1`: a new test beside a
  changed one ("Added 1 test." VERIFIED); a test moved to another file; a test moved from a class to module level; a
  test deleted and a new one of its name ("Added 0 tests." VERIFIED); a renamed class above unchanged tests and a test
  name defined twice in one scope (the two families of section 1), each decided by the truth; a file that does not
  parse on either side, a `def test_` in a Markdown file, a type change (status T), a NAME added as a class where the
  claim says function: each unchanged.
- **G-P3 (nothing else moves).** Every pinned pair (`check_pairs.js` and the Python pair tests) reads as on
  `45f351d1`, and over the G-P4 cases the text door's claims, verdicts and reasons equal `45f351d1`'s: 0 differences.
- **G-P4 (the differential).** `web/gate/differential/path2b_fuzz.py` with its case generator as committed at
  `164799b6`, its score of `symbol_added` made to read the kind as section 2 says and nothing else in it changed,
  every case run through the git door on a two-commit repository, seed 3 (not run before signing),
  30,000 cases on each of CPython 3.9 to 3.14: 0 decided verdicts that differ from the truth, and at least 5,000
  decided verdicts per runtime, so that a door that decides nothing cannot pass.
- **G-P5 (suite, demo, bookmarklet).** Every diffgate test module and every test importing `styxx.diffgate` or
  reading `web/gate` is green, but for the four failures that fail on `45f351d1` too on CPython 3.13 (two in
  `tests/test_prereg_ci_result.py`, one in `tests/test_sworn_action.py`, and `test_validate_probe_smoke`, which needs
  scikit-learn); the overlay's reconstruction test is extended to drop R-101c's block and hook and still reach
  main's bytes; `--demo` prints the same bytes; `build_bookmarklet.py --check` matches.

### No corpus gate

The EXTERNAL-1 shelf holds diffs, not repositories, and is not in this checkout; the git door cannot read it. The
result of this freeze covers generated cases only, and says so.

## 6. The gates block

```gates
{"gates": {"G_P1": {"power_basis": "a pass or fail of fixed tests on the issue's reproduction, so no sample and no power",
                    "metric": "result.unit.p1_issue_pass", "op": ">=", "value": 1,
                    "metric_means": "1 if the three claims read as section 5 says at both doors"},
           "G_P2": {"power_basis": "one probe per family PATH-2b's run and #161's passes found; a fixed list, no sample",
                    "metric": "result.unit.p2_families_pass", "op": ">=", "value": 1,
                    "metric_means": "1 if every G-P2 probe reads as section 5 says at the git door"},
           "G_P3": {"power_basis": "section 4: the text door, the port and the bookmarklet cannot move, so any difference is a defect and the bar is zero",
                    "metric": "result.unit.p3_text_door_differences", "op": "<=", "value": 0,
                    "metric_means": "pinned pairs and G-P4 cases where the text door's claims, verdicts or reasons differ from 45f351d1's"},
           "G_P4": {"power_basis": "section 7 allows no false decided verdict, so the bar is zero; with at least 5,000 decisions per runtime and none false, the false rate is below 0.06% at 95% (three over the decisions); PATH-2b's git door decided 153 of 300 cases, about half",
                    "metric": "result.unit.p4_false_decided", "op": "<=", "value": 0,
                    "metric_means": "decided verdicts at the git door that differ from the truth, summed over CPython 3.9 to 3.14"},
           "G_P4_YIELD": {"power_basis": "a floor at a third of the decision rate PATH-2b's git door showed (153 of 300), so a door that decides nothing fails",
                          "metric": "result.unit.p4_min_decided_per_runtime", "op": ">=", "value": 5000,
                          "metric_means": "the fewest decided verdicts at the git door on any one runtime, over 30,000 cases"},
           "G_P5": {"power_basis": "PATH-2b's G-P5, with the reconstruction test extended",
                    "metric": "result.unit.p5_suite_green", "op": ">=", "value": 1,
                    "metric_means": "1 if the suites, the demo bytes and the bookmarklet check all pass, but for the four named failures that fail on 45f351d1 too"}},
 "outcomes": [{"when": {"G_P1": false}, "verdict": "BLOCKED__g_p1_failed"},
              {"when": {"G_P2": false}, "verdict": "BLOCKED__g_p2_failed"},
              {"when": {"G_P3": false}, "verdict": "BLOCKED__g_p3_the_text_door_moved"},
              {"when": {"G_P4": false}, "verdict": "NOT_LANDED__a_git_door_verdict_is_false"},
              {"when": {"G_P4_YIELD": false}, "verdict": "NOT_LANDED__the_git_door_decides_too_little"},
              {"when": {"G_P5": false}, "verdict": "BLOCKED__g_p5_failed"},
              {"when": {"G_P1": true, "G_P2": true, "G_P3": true, "G_P4": true, "G_P4_YIELD": true, "G_P5": true},
               "verdict": "LANDS__r101c_decides_at_the_git_door"}],
 "smoke_verdict": "INVALID__smoke_plumbing_only"}
```

Rows are read in order and the earliest whose `when` holds gives the verdict.

## 7. The merge bar

No claim reads worse than on `45f351d1` with the overlay, at either door, judged against the truth; nothing moves at
the text door, in the Action, the port or the bookmarklet. A restored VERIFIED that is false is worse.

## 8. The operator's choice

None is left open: section 3 fixes the scope (git door only, the Action and the port unchanged), section 5 the bar.
The operator signs this file as written, or says what to change before signing.

## 9. What is not claimed

No precision figure on real pull requests; nothing about the text door, which still withholds #101 claims; #97 and
#121 stay open; nothing restores a licence #161 withdrew; no committed receipt, PREREG, RESULT or NOTE is edited.

## 10. What failure means

A failure of G-P1, G-P2, G-P3 or G-P5 blocks the branch, and the overlay stays as it is. A failure of G-P4 means a
restored verdict is false, and one of G-P4_YIELD that the door decides too little to be worth its code: in either
case the branch does not land.

## Signature

Signed by the operator, flobi, in the project chat on 2026-11-19 at 18:28:10Z, answering the lead's post of
17:04:42Z that put this file's scope, bar and limit: "Sign c". Section 8 left no option open, so the file is signed as
written. Nothing else in this file changes at signing.
