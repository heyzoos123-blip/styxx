# REFUTATION — the header/line gap is mostly token kind — sworn, 2026-09-02

Fathom Lab · 2026-09-02 · closed-model-frontier · **The first sworn refutation in this tree.**
A statistical referee objected to `RESULT_handedness_v3_header_handed_2026_09_02.md`. The
objection is a set of numbers, so it is held to the author's standard: the harness ran the
referee's re-derivation script and minted what it printed, and every number below binds to one
of those receipts or to the result under attack. Manifest:
`turn_2026_09_02_refutation_v3_kind.manifest.json`; verifier at commit `37c7bdcbbea5`.

## The claim under attack

<sworn r="path:papers/closed-model-frontier/RESULT_handedness_v3_header_handed_2026_09_02.md#L1" k="quote">The result whose title says `an accusation handed by a table header is true`</sworn>. Its cells: header-handed accusations genuine at
<sworn r="path:papers/closed-model-frontier/handedness_v3_result.json#/cells/header/genuine_share" k="numeric">0.9515</sworn> and line-handed at
<sworn r="path:papers/closed-model-frontier/handedness_v3_result.json#/cells/line/genuine_share" k="numeric">0.6391</sworn>, read as structure handing a truer target than
co-occurrence.

## The refutation, re-derived by the harness

The harness ran <sworn r="r1" k="quote">`python papers/closed-model-frontier/handedness_v3_stratified.py --emit-json`</sworn>
against the committed rows. It printed: the header cell is
<sworn r="r30" k="numeric">0.8606</sworn> decimals; within decimals the cells are
<sworn r="r7" k="numeric">1.0</sworn> against
<sworn r="r19" k="numeric">0.9605</sworn>; within integers,
<sworn r="r10" k="numeric">0.6522</sworn> against
<sworn r="r22" k="numeric">0.321</sworn>. The raw difference of
<sworn r="r26" k="numeric">0.3124</sworn> becomes
<sworn r="r27" k="numeric">0.117</sworn> kind-adjusted, under the
<sworn r="r31" k="numeric">0.15</sworn> the preregistration froze for the raw one.

## What this refutation does and does not do

It does not touch the verdict, which was scored on the raw difference as frozen. It withdraws
the reading. It rests on the same one-family panel as the result and inherits that boundary. And
it is the shape every refutation in this lab now takes: a referee who says a number ships the
script that produces it, the harness records what the script printed, and the critic swears to
the same kind of receipt the author did.

---

*A claim was sworn. Its refutation is sworn. The reader needs neither author's word.*
