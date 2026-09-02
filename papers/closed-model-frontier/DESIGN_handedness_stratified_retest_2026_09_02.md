# DESIGN — the kind-stratified re-test the header-handed result now owes — 2026-09-02

Fathom Lab · 2026-09-02 · closed-model-frontier · **A design, not a preregistration.** It is
written so that the fresh draw and the three blind seats PREREG_S1 (sworn spans) is being frozen
around can score this too, from the same corpus and the same seats, without a second panel.

## Why

`RESULT_handedness_v3_header_handed_2026_09_02.md` scored HEADER_HANDED_ACCUSES_TRUER on the raw
difference of genuine-accusation shares, 0.9515 header-handed against 0.6391 line-handed. Its
referee addendum, re-derived from the committed rows, shows the header cell is 86% decimals and
that within decimals the two cells are 1.000 and 0.961; kind-adjusted, the difference is 0.117,
under the 0.15 the preregistration froze for the raw difference. The mechanism reading — that a
label the author committed to hands a truer target than a co-occurring word — is therefore
unsupported *as against token kind*, and the 2026-08-27 panel it rests on was one model family
whose sanity gate failed at 0.4933. Both defects are fixed by the same instrument PREREG_S1
needs: a fresh draw and seats that are not one family.

## The contrast, stratified at the design stage

Population: every accusation OATH makes on the fresh external corpus (repositories disjoint from
the 2026-08-27 set and from the 2026-08-31 corpus), certified at the verifier build named in the
preregistration, joined to `binding_context.header_bound` per token (the v3 join rule, frozen).

Strata, by the token's printed form, declared before the draw: **decimal** (contains `.`),
**integer** (digits only), **comma-number**. Cells: header-handed against line-handed *within
each stratum*. Range-sanity tokens are excluded from both cells (they report, not accuse, under
V14) and counted separately.

Seats: three blind adjudicators of at least two model families, the key sealed before the draw,
decoys as in PREREG_S1, the same 30-of-30 decoy gate or the run is void.

## Gates, as this design would freeze them

- `G_P_decoys`: 30/30 decoys correct, else VOID.
- `G_N_strata`: at least 40 tokens in each of the two cells of the **integer** stratum and of the
  **decimal** stratum, else INVALID__strata_too_thin (the v3 cells had 23 and 81 integers; a
  re-test that cannot fill them tests nothing).
- `G_K_kind_adjusted`: Mantel-Haenszel-weighted difference of header minus line genuine share
  across strata >= 0.15 — the same bar v3 froze for the raw difference, now applied where it
  should have been.
- `G_I_integers`: header minus line within integers >= 0.15 (the stratum where v3's residue
  lived, 0.652 against 0.321).
- `G_D_decimals_ceiling`: reported, not gated: decimals are near ceiling in both cells and a
  difference there cannot be read.

Outcomes: decoys fail → VOID; strata thin → INVALID; `G_K` and `G_I` both true →
HEADER_HANDED_TRUER__against_kind; `G_K` true, `G_I` false → HEADER_HANDED_TRUER__decimals_only
(a form effect, retire the mechanism reading); `G_K` false → NOT_HEADER_HANDED__kind_explains_it
(retire it and say so in the synthesis).

## What this does not fix

Repository concentration: v3's header cell drew 119 of 165 tokens from one model card. The
design caps any one repository at 25% of either cell after the draw, declared here so that the
cap is not chosen after seeing which repository would flip the verdict. And a panel of models is
still a machine's opinion about a machine; the human seats DESIGN_sworn_measurement names remain
owed for the sworn-span question, and this re-test inherits that boundary.
