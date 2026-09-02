# AGENT REPORT — round 2026-09-02 on `claude/styxx-work-gyunvn`, sworn — 2026-09-02

Fathom Lab · 2026-09-02 · **The first sworn agent report for coding work in this tree.** The
agent that did the round wrote this; the receipts it swears to were minted by
`styxx/sworn_harness.py` from the commands it names, at the head this report describes, commit
`f93beee9751f`. Nothing numeric below was typed from memory. Manifest:
`turn_2026_09_02_agent_report.manifest.json`; its legend says what each `rN` is.

## What changed

Against fathom-lab main `28ae2d0a`, the branch carries
<sworn r="r4" k="numeric">42 commits</sworn>. The diff touches <sworn r="r9" k="numeric">92 files</sworn>, with
<sworn r="r10" k="numeric">26133 insertions</sworn> and <sworn r="r11" k="numeric">111 deletions</sworn>. The changed-file list
includes <sworn r="r13" k="quote">the verifier at `styxx/certify.py`</sworn> and
<sworn r="r13" k="quote">the new `styxx/sworn_harness.py`</sworn>. It does not include
<sworn r="r13" k="absent">`OATH_CONTRACT.md`</sworn>: the range-sanity flag ships OFF and the contract sentence it
owes is the release cycle's, not this round's.

## What was verified, and how it went

The full suite, run by the harness on this machine: <sworn r="r20" k="numeric">3657 passed</sworn>,
<sworn r="r21" k="numeric">2 failed</sworn>, <sworn r="r22" k="numeric">50 skipped</sworn>, <sworn r="r23" k="numeric">4 xfailed</sworn>; pytest exited
<sworn r="r19" k="numeric">1</sworn>. Both failures are one error, <sworn r="r17" k="quote">`No module named 'transformers'`</sworn>:
torch is installed here without the NLI stack, so two tests that CI's lean environment skips run
and fail on the import. That is an environment fact, sworn to the same stdout as the counts.

Lint, as CI runs it (`ruff check styxx`): exit <sworn r="r26" k="numeric">0</sworn>, and it printed
<sworn r="r24" k="quote">`All checks passed!`</sworn>. Lint over the whole tree (`ruff check .`), which CI does not
run: exit <sworn r="r16" k="numeric">1</sworn>. The findings are in paper scripts and old tooling outside the
package; this report does not claim they are clean.

## One number from the science, in the other receipt form

The round's sharpest result, at this commit: accusations the verifier was handed by a table
header were genuine at <sworn r="path:papers/closed-model-frontier/handedness_v3_result.json#/cells/header/genuine_share" k="numeric">0.9515</sworn> on the external blind
panel, against <sworn r="path:papers/closed-model-frontier/handedness_v3_result.json#/cells/line/genuine_share" k="numeric">0.6391</sworn> for line-handed ones. Same
document, two receipt forms: `rN` from the harness for what the tools printed, `path:` at a
commit for what the experiments wrote.

## The boundary, stated

The harness ran after the agent's turn and inside the agent's working tree, so the manifest
records no `authored_sha256`; invariant 2 rests on `kind_of_source` and on the committed harness
script anyone can re-run. The agent had write access to the manifest file. In the deployment this
report is a rehearsal for, the harness runs in CI on the pull request head, where the agent has
no write access, and the verifier gates the merge on the PR description's sworn spans against
that manifest. See `DESIGN_agent_that_swears_2026_09_02.md`.

---

*An agent finished a task and reported on it. Every number in the report is bound to what a tool
printed, and the two failures are in it because the receipt has them.*
