# DESIGN — the agent that swears: sworn output for coding work — 2026-09-02

Fathom Lab · 2026-09-02 · A design, with one rehearsal in the tree
(`AGENT_REPORT_round_2026_09_02.md`). Nothing here is a measurement.

## The problem in one paragraph

A coding agent finishes and reports: the suite passes, three files changed, the migration is
safe. Every instrument this lab built to *find* the claims in that prose was measured against
strangers and did not survive it (`CENSUS_prose_claimhood_instruments_2026_09_01.md`). Sworn
output (`SPEC_sworn_output_v01_2026_09_01.md`) removes the finding: the author binds a sentence
to a receipt at write time and the verifier re-derives it. For research documents the receipts
are files at a commit. For coding work the receipts are what the tools printed, and invariant 2
says the agent cannot mint them. `styxx/sworn_harness.py` is the harness that can.

## What the harness mints

For every command it runs: stdout, stderr, exit code. For commands in its fixed extractor table:
the scalars a report wants — pytest's passed, failed, skipped and xfailed; `git diff
--shortstat`'s files, insertions and deletions; `git rev-list --count`'s commit count. For a diff:
the full patch bytes (for `hash`) and the changed-file list (for `quote` and `absent`). Every kind
is in the spec's external vocabulary; the harness cannot mint an author-side kind. A legend beside
the manifest says what each `rN` is; the verifier never reads it.

## The threat this closes, and the one it does not

**Closed: author-owned extraction.** If the agent supplied the pattern that pulls "3 files
changed" out of a tool's output, it could supply one that finds the number it wants. The extractor
table is fixed in the harness source and keyed by the command's shape; a command the harness does
not know yields bytes and an exit code, and the author may swear to those and to nothing else.

**Not closed here: the manifest file itself.** In the rehearsal the harness ran inside the
agent's working tree, after the turn, with the agent holding write access to the manifest. The
manifest records no `authored_sha256` for the same reason `harness_pytest.py` records none. The
committed harness is a script anyone can re-run against the same commit; that re-run, not the
committed file, is the receipt's authority. The rehearsal says so in its own boundary section.

## The deployment this is a rehearsal for

1. The agent opens a pull request. Its description is a sworn document: every count, every test
   result, every "this file was not touched" is a span bound to an `rN`.
2. CI mints the manifest on the PR head — the agent has no write access there — by running the
   harness over the commands the repository's policy names: the suite, the lint, the diff against
   the base, the commit range.
3. CI verifies the description against that manifest and posts the verdict receipt. SWORN-HELD
   is a description whose numbers are what the tools printed. SWORN-FAILED names the span.
   UNSWORN is a description that committed to nothing, and it is not "no failures".
4. The merge gate reads the verdict. A reviewer reads the narrative knowing which sentences are
   bound.

That is the whole mechanism. No model reads the description to decide what is a claim; the
author decided, at write time, and the harness disposes.

## Owed to v0.2

- **`exec` kind:** a span that swears to the command's identity, not only to its output, so a
  reader can tell "the suite" from "the three tests the agent chose". Reserved in v0.1, MALFORMED
  there by design. *Addendum, later the same day:* v0.1 already covers the identity without a new
  kind — the harness now mints each command line as its own `harness_note` receipt, first, and
  the author quotes it (`k="quote"`). What `exec` would still add is the verifier checking that
  the quoted command is the one whose stdout the next span cites; that binding stays owed.
- **The legend inside the manifest,** covered by the digest, so what an `rN` is cannot drift from
  what it holds.
- **A `>` inside a receipt.** v0.1's lexer closes the tag at the first `>`, so a JSON-pointer key
  containing `>` (a transition table's `header->incidental`) cannot be sworn to; the sidecar
  refuses, correctly. v0.2 owes an escape, or a rule that receipt keys are URL-encoded. Met on
  2026-09-02 while swearing `RESULT_handedness_v4_INVALID`; the keys were renamed.
- **Exponent notation.** A receipt leaf like `1.36e-05` cannot be sworn as `numeric` in v0.1; the
  printed-decimal grammar is deliberate (no float, no search), and a scientific form is owed a
  rule of its own. Met 2026-09-02 swearing the pMNIST RESULT; the values were cited, not sworn.
- **Multi-line needles** for `quote` and `absent` over file lists; v0.1's needle is one inline
  code span, on purpose, and a file list wants more.
- **Measurement.** `DESIGN_sworn_measurement_2026_09_01.md` names the seats this needs: bound
  recall, trivial swearing, and coverage error, judged by people who are not the author. A
  rehearsal in the author's own tree is not that measurement, and this design does not claim it.
