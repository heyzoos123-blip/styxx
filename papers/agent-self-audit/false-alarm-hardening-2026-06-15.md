# False-alarm hardening sprint — 2026-06-15

A recursive-integrity pass: the styxx false-alarm machinery turned on the
styxx instruments themselves. Triggered by the agent self-audit, which showed
the cognometric gate firing `needs_revision` on essentially all benign output.
Every change below ships with a committed receipt and a regression guard; two
proposed changes were **rejected by their own acceptance gates** and are
recorded as negative results.

All work is on branch `claude/fathom-styxx-remote-access-e9jgk8`. Full suite
after the sprint: **975 passed, 18 skipped**; the only failures are the
pre-existing centroid SHA-pin mismatch (see §Open).

## What was wrong, and what fixed it

### 1. The gate fired on everything (construct-ceiling-aware gate)
Text-only overconfidence is a documented construct ceiling (held-out AUC
0.57–0.60 < 0.70 bar) that reads stated-confidence *register*, not
calibration — so it pinned ~0.95 on plainly true text. Because it was both
averaged into the composite and able to trip the `any(axis > 0.60)` clause, it
forced `needs_revision=True` on benign output (a `HEARTBEAT_OK` ping, "the
answer is 4"). Fix: `needs_revision` is decided over the **gate-eligible
(discriminative) axes only**; construct-ceiling instruments are reported but
don't vote. **Receipt:** false-alarm on confident benign statements
**100% → 1.9%**, sycophancy recall preserved (`scripts/self_audit/gate_false_alarm_eval.py`).

### 2. The recovery narrative misreported noise as evidence
`recover_posture()` printed the reference-less deception mean (the
`HEARTBEAT_OK`≈0.99 noise) and the saturated overconfidence mean as plain
numbers an agent would read as real signal. Fix: construct-ceiling firings are
marked inline (`deception=0.68 [reference-less — non-discriminative]`), and the
overconfidence ceiling heuristic became mode-aware so reference-grounded
overconfidence is **not** mislabeled "register, not calibration".

### 3. The sycophancy instrument over-fired (three layers)
- **Substring matching** counted "agree" inside *disagree*, "correct" inside
  *incorrect*, "right" inside *copyright* — the negation of agreement scored
  *as* agreement. Fixed with word-boundary matching.
- **"compelling"** (superlative lexicon, highest model coefficient) described
  *arguments*, not the user — 7 pos / 15 neg on the seeds. Dropped.
- **"right"/"correct"/"true"** were non-discriminative as bare words ("a right
  triangle" scored identically to "you're so right"). A due-diligence pass
  caught that the seed corpus *couldn't see this* (its negatives never use the
  words as content), so the corpus was de-biased with a labeled content-word
  negative set, and the words were made **context-gated** (count only after an
  agreement cue / clause-initial / exclaimed). Adversarial stress-testing of
  that fix then caught a symmetric FP from the possessive "your" ("your right
  hand"), which was dropped from the cue set.

**Receipt** (`scripts/self_audit/sycophancy_precision_eval.py`): seed AUC
**0.881 → 0.94**; content-word false-positives **100% → 0%**; combined
false-positive (seed + content) **66% → 13%**; recall 0.88 → 0.82 (bounded,
documented). Known residual: terse copula agreements hinging on "is" ("Your
analysis is right") evade, since "is" can't be a cue without re-flagging "it
is true that …" — a lexical-disambiguation limit, not a bug.

### 4. Reference-grounded overconfidence (new capability)
Turned the construct-ceiling instrument into a discriminative one, mirroring
deception's NLI grounding: `grounded_overconfidence = register × P(contradiction)`.
Confident+wrong → high, confident+correct → ~0, hedged+wrong → low. **Receipt:**
mechanism AUC **0.52 → 1.00** on the factual triples
(`scripts/self_audit/overconfidence_grounding_eval.py`, contradiction oracle;
live contradiction = deception_v2 NLI, AUC 0.818, backend-gated). Re-enters the
gate only when grounded; backend-less behavior is unchanged.

### 5. Portability
`styxx/scan.py` embedded `\u` escapes inside f-string expressions — a
SyntaxError on Python 3.9–3.11 (all advertised-supported). Hoisted to named
constants.

## Negative results (rejected by acceptance gates)
- **Retraining the sycophancy weights** on the corrected features improved
  in-corpus CV AUC 0.972 → 0.986 but *lowered* the independent seed AUC
  0.938 → 0.927 — overfitting. Kept the v0 weights.
  (`scripts/self_audit/sycophancy_retrain_v02.py`.)
- **Changing the deception-v0 / refusal lexicons**: deception's single-word
  matching is already token-based; refusal's single-word terms are likely
  intentional stems and there is no labeled corpus to validate a change. Left
  unchanged.

## Durable guards added
- Per-instrument regression guards (gate false-alarm ≤ 20%; sycophancy AUC ≥
  0.92, content-word FP ≤ 10%).
- A **pipeline-level** benign-text benchmark (`benchmarks/data/benign_text_corpus_v0.jsonl`,
  n=20) + `tests/test_benign_false_alarm.py`: the full `preflight()` gate stays
  quiet (0/20) across all benign-text classes a caller experiences.

## Open (needs a human decision)
**Centroid SHA-pin mismatch.** `styxx/centroids/atlas_v0.3.json` hashes to
`eda49b87…`, but `vitals.py` and `papers/cognitive-metrology-v1.md` pin/cite
`502313c2…`. Both the pin and the file entered in the same 7.4.1 commit,
already inconsistent — a packaging mistake, not tampering. The canonical
`502313c2` file is recorded nowhere and is not recoverable from the repo or the
release bundle; both the Python and JS packages ship the same valid, complete
`eda49b87` file. Resolution requires either (a) confirming `eda49b87` is the
intended final table and updating the pin **and** the paper's cited hash, or
(b) restoring the `502313c2` file from the external archive. Not actioned: it
is a tamper guard and a published claim.
