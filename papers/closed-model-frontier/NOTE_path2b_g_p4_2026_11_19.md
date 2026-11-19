# NOTE — PATH-2b: R-101b as frozen fails its own gate G-P4 at the text door

## 0. Status

2026-11-19. Branch `fix/diffgate-101-path2b`, from the seal commit `2f671d41` of
`PREREG_path2b_changed_def_2026_11_19.md` (signed "Sign b", option B). This note records a gate run; it edits no
PREREG, RESULT or NOTE, and it is not a RESULT: the gates were not all run (section 3), so the fence's verdict row is
not read here.

## 1. What was run

R-101b as section 3 of the plan words it, in `styxx/diffgate.py`, after the PATH-2a overlay and outside its block:

- the text door (`gate_diff_text`) reads the diff alone under K (`_p2b_parse`, `_p2b_read_section`) and decides
  "`n = net` → VERIFIED" for `tests_added` and "added more times than removed at one qualified name → VERIFIED" for
  `symbol_added`;
- the git door (`gate_diff`) reads the base and head blobs of the `.py` and `.pyi` paths the diff touches and decides
  by `ast` (option B).

K is read at least as strictly as the plan words it: besides K1 to K5, a tokenizer of strings, brackets and comments
(`_p2b_lex`) must find every relevant line at a statement start, and the triple-quote parity of K3 must hold too.

The differential is `web/gate/differential/path2b_fuzz.py`: base and head test files built from the plan's probe
families and random edits (a changed signature, an added test of a new or a used name, a deletion, a rename, a
renamed class, a test moved between a class and module level or to another file, an unrelated line at the top, a
long unchanged tail), the diff written in git's header form at context 0, 1, 3, 5 or the whole file, and summaries
"Added k tests." for every k from 0 to one past the count and "Adds function NAME." for names the head defines.
Every verdict R-101b decides (a reason ending "(#101)") is scored against the plan's truth, read by the script's own
`ast` walk from the two files.

    python web/gate/differential/path2b_fuzz.py --cases 30000 --seed 1 --git 300

Each runtime's report, with up to six false cases written out, is in `path2b_g_p4_runs/`.

## 2. What it found

The same on CPython 3.9.25, 3.10.20, 3.11.18, 3.12.3, 3.13.18 and 3.14.6:

| | cases | claims read | decided | decided and false |
|---|---|---|---|---|
| text door | 30,000 | 150,557 | 2,448 `tests_added`, 71 `symbol_added` | 174 (all `tests_added`) |
| git door | 300 | | 153 | 0 |

Over `git diff` of the same 300 cases, the two doors differ on 2 claims the text door decided: it read
"Added 1 test." VERIFIED where the git door kept the overlay's UNCHECKABLE. G-P4's bar is 0 decided verdicts that differ from truth, so **G-P4 fails**, and by section 10 the
corpus run is blocked and the overlay stays as it is.

Why, read from the false cases. A diff shows part of a file, and K makes the part start at line 1 but cannot make it
reach the end. Of the 174, 136 are cases where a line that opens a scope changed (a renamed `class`, a test moved out
of a class) and tests the diff shows as unchanged context, or does not show at all, change qualified name with it;
the other 38 are cases where a test name is defined twice in one scope, in the lines shown or in lines below them, so
a test the added lines count is not a new name. The truth of section 2 is a set of qualified names, and neither
reading can be had from a diff that stops before the end of the file. Exploratory variants run on seed 2 (6,000 cases,
not a gate): requiring the scopes to read alike on both sides cut the false decisions to 7; deciding only
`net = 0` as well cut them to 1, a renamed class in another Python file of the same diff. Only the git door reads the
whole files.

## 3. What was not run

- The port (`web/gate/diffgate.js`) was not written: G-P4 fails on the Python side alone, which blocks whatever the
  port does.
- G-P1 and G-P2 were read on the Python text door only (`tests/fixtures/path2a_repros.json`); the issue's
  reproduction there begins at line 1, unlike section 5's wording, and reads as on `45f351d1` with "Added 0 tests."
  VERIFIED.
- G-P5 was not run to completion; `tests/test_diffgate_path2a.py::test_reconstruction_python` fails, since the doors'
  hook lines changed.
- The corpus gates: `external1_shelf.sqlite` is not in this checkout.

## 4. What follows

The git door decided 153 times without a false verdict. A further freeze that keeps the text door, the Action and the
port as on `45f351d1` and lets only the git door decide, by `ast` over the two commits' files, is the repair this run
supports. It needs the operator's signature before any of its code.
