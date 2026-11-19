# RESULT — PATH-2c: R-101c decides at the git door, 14,715 verdicts per Python version and none false

Fathom Lab · 2026-11-19 · Plan `PREREG_path2c_git_door_2026_11_19.md`, signed "Sign c" at 18:28:10Z (commit
`92934b6d`) and sealed (`434eb820`, blob `b707bebe…`) before any code of the repair. Branch
`fix/diffgate-101-path2c`. Receipt `path2c_receipt_2026_11_19.json`, scored by `styxx.prereg_ci`'s `rescore` against
the plan's gates block: **`LANDS__r101c_decides_at_the_git_door`**, row 7, every gate true.

## What changed

`styxx/diffgate.py` is `45f351d1`'s file (sha256 `80d0e79e…`) and two things more: a block after the PATH-2a
overlay's END marker, and a hook in `gate_diff` that hands the overlay's result to it (sha256 `6cebd299…`). The
overlay's block is not edited, `gate_diff_text` is not edited, and the port, the bookmarklet and the GitHub Action
are not edited. At the git door, a `tests_added` or `symbol_added` claim the overlay withheld for #101 with the phrase
`tests`, `split`, `redefined`, `symbol` or `again` is read against the plan's truth: the base and head blobs of every
`.py` and `.pyi` path in `git diff --name-status -z --no-renames`, parsed by the running CPython's `ast`. It moves
from UNCHECKABLE to VERIFIED, with a reason ending `(#101)`, where the truth's count equals the claim's (and is no
more than the lines main counted), or where NAME is newly defined as the claim's kind; otherwise it stays as it was.
Any status other than A, D or M on such a path, a blob that cannot be read, a file that does not parse, a counted
line outside a Python file, or a repository that cannot be read decides nothing. No CONTRADICTED is added.

## The gates

| gate | bar | measured |
|---|---|---|
| G-P1, the issue | three claims as section 5 says, at both doors | pass (`tests/test_diffgate_path2c.py`) |
| G-P2, the families | each probe matches the truth or reads as on `45f351d1` | pass, 17 tests |
| G-P3, nothing else moves | 0 differences | 0: 190 pinned pairs; 301,264 text-door lines over the G-P4 cases |
| G-P4, the differential | 0 decided verdicts that differ from the truth | 0, on each of six Python versions |
| G-P4_YIELD | at least 5,000 decided per Python version | 14,715 on each |
| G-P5, suite, demo, bookmarklet | green but the four named failures | pass |

**G-P1 and G-P2.** Each probe is a two-commit repository, read at both doors and held to `45f351d1`'s own reader,
which the test builds from this file with R-101c's block and hook cut: the text door reads alike, and at the git door
a claim reads alike or moves only from the overlay's UNCHECKABLE to VERIFIED. On the issue's reproduction "Added 0
tests." reads VERIFIED at the git door; "Added 2 tests." and "Adds function backoff with jitter." stay withheld.

**G-P3.** `check_pairs.js` reads 190 pinned pairs with 0 disagreements, and the Python pair tests pass.
`web/gate/differential/path2c_text_same.py` builds the G-P4 cases with the same draws as the G-P4 run and reads every
summary through the text door over the generator's diff and over `git diff` of the same repository: on `45f351d1`'s
tree and on this branch, 30,000 cases, 301,264 lines, both sha256 `f4bb76ab850fb02c…`.

**G-P4.** `web/gate/differential/path2b_fuzz.py` with its generator as at `164799b6` and its score of
`symbol_added` made to read the kind (section 2), and nothing else changed:

    python web/gate/differential/path2b_fuzz.py --cases 30000 --seed 3 --git 30000

The same on CPython 3.9.25, 3.10.20, 3.11.18, 3.12.3, 3.13.18 and 3.14.6 (`path2c_g_p4_runs/`):

| | cases | claims read | decided at the git door | decided and false |
|---|---|---|---|---|
| each Python version | 30,000 | 150,632 | 14,715 | 0 |

The text door decided nothing, as on `45f351d1`. With 14,715 decisions and none false, the false rate on these cases
is below 0.021% at 95% (three over the decisions), per Python version. The runs set `GIT_TEMPLATE_DIR` to an empty
directory, which leaves git's hook samples out of each repository and changes no commit.

**G-P5.** Every test module that names `styxx.diffgate` or reads `web/gate` (51 files): green but
`tests/test_sworn_action.py::TestTheCommittedSample::test_the_committed_sample_reproduces`, which fails on
`45f351d1` too. `--demo` prints `45f351d1`'s bytes. `build_bookmarklet.py --check` matches, with terser 5.51.2.
`tests/_p2a_ref.py` cuts R-101c's block and hook before it reads the reader, so the overlay's reconstruction still
reaches main's bytes.

## What else moved, and why

- `web/gate/differential/py_side.py` pins the new file, as its own comment records for `fetch_pr`: the hash moved
  and no verdict at the text door did. `web/gate/README.md` names both files and the pin.
- `tests/test_port_is_current.py` holds the port and the README to the reader with R-101c cut, which is the file the
  port transliterates; any other change to the reader still moves that hash.
- A record's `build` names the new file's hash, at both doors.

## What was found and is not repaired

A claim the overlay does not withhold can read wrong against the truth, and R-101c cannot move it (section 4). In one
probe git's diff aligns an unchanged `def test_b` as added, so main reads "Added 0 tests." CONTRADICTED and the overlay
keeps it, where the truth is 0. `test_a_claim_the_overlay_does_not_withhold_stays_as_on_main` pins it as it is.

## What is not claimed

No precision figure on real pull requests: the cases are generated, and the EXTERNAL-1 shelf holds diffs, not
repositories, so there is no corpus gate. Nothing at the text door, in the Action, the port or the bookmarklet, which
still withhold #101 claims. #97 and #121 stay open; no licence #161 withdrew is restored; no committed PREREG,
RESULT, NOTE or receipt is edited.
