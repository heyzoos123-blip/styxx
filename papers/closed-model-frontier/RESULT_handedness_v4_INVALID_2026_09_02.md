# RESULT — token-level h, v4: the author's own label — INVALID, one row under a plumbing bar — 2026-09-02

Fathom Lab · 2026-09-02 · closed-model-frontier · Preregistration:
`PREREG_handedness_v4_own_label_2026_09_02.md` (commit 7f96cd73). Receipt: `handedness_v4_result.json`
at `77bebe6d5377`. **Verdict, as scored under the frozen gates:**
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/verdict" k="quote">`INVALID__operationalization_failed_plumbing`</sworn>.

## What failed

The plumbing gate `G_P_rowlabel` asked the definition to move at least 20 of the line cell's
table rows to STRUCTURAL; it moved
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/metrics/line_table_rows_reclassified_structural" k="numeric">19</sworn>. The bar was this author's
guess at the definitional referee's count of 32 row-label rows, and the definition as frozen —
a trigger in the token's own column header or its own row label — found 19 of them. One row.
The preregistration's rule is that a bar does not move after data, and a plumbing bar is a bar.
INVALID ships as INVALID.

Every other plumbing check passed: <sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/metrics/docs_missing" k="numeric">0 documents missing</sworn>
from the hash-verified cache, and the eight header-cell false accusations of v3 all landed in
INCIDENTAL by the definition alone
(<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/metrics/eight_named_rows_not_incidental" k="numeric">0</sworn> misplaced).

## What the frozen substantive gates would have read — reported, not a verdict

Under the own-label split the structural cell holds
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/cells/structural/n" k="numeric">89 rows</sworn> at
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/cells/structural/share" k="numeric">0.9888</sworn> genuine and the incidental cell
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/cells/incidental/n" k="numeric">245 rows</sworn> at
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/cells/incidental/share" k="numeric">0.7224</sworn>; with the largest repository dropped, the difference
is <sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/metrics/delta_ex_top_repo" k="numeric">0.3528</sworn>, over the 0.15 bar. Kind-adjusted across
decimal, integer and comma strata over all repositories, the difference is
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/metrics/kind_adjusted_delta_all" k="numeric">0.0662</sworn>, under the same bar. Within decimals the
cells are <sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/by_kind/structural/decimal/share" k="numeric">1.0</sworn> against
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/by_kind/incidental/decimal/share" k="numeric">0.9778</sworn>; the structural cell is
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/by_kind/structural/decimal/n" k="numeric">83</sworn> decimals of 89, and its integer stratum holds
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/by_kind/structural/integer/n" k="numeric">6</sworn> tokens. Had the plumbing gate passed, the
outcome table names this `OWN_LABEL__form_confounded`. It did not pass, and this paragraph is
what the receipt shows, not what the preregistration licenses.

## What the re-split did to v3's cells

Of v3's 165 header-handed rows, <sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/v3_cell_by_v4_cell/header_to_incidental" k="numeric">95</sworn>
moved to INCIDENTAL: their own column label carried no trigger; the word that obligated them
lived in another column. Of the 169 line-handed rows,
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/v3_cell_by_v4_cell/line_to_structural" k="numeric">19</sworn> moved to STRUCTURAL on their own row
label. The split the receipt draws most sharply is the one the definitional referee named:
table rows are genuine at <sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/table_vs_prose/table/share" k="numeric">0.934</sworn>
(<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/table_vs_prose/table/n" k="numeric">197</sworn>) and prose lines at
<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/table_vs_prose/prose/share" k="numeric">0.5912</sworn>
(<sworn r="path:papers/closed-model-frontier/handedness_v4_result.json#/table_vs_prose/prose/n" k="numeric">137</sworn>) — genre, which the synthesis had demoted to a proxy.

## Reading, bounded

Two referees and two runs now agree from different directions: on these receipts, "who handed
the target" separates accusations mostly by token kind and by genre, and the residue that could
be called structure is a sliver inside a near-ceiling decimal stratum. The mechanism reading in
`SYNTHESIS_the_grain_of_the_handed_target_2026_09_02.md` is withdrawn to that; the h-mapping's
grain stays a declaration. What would test structure properly is
`DESIGN_handedness_stratified_retest_2026_09_02.md`: a fresh draw, seats of more than one model
family, strata declared before the draw. Nothing here licenses the accusing branch.

---

*The bar was one row too high and the definition was one row too honest. Under it, the author's
own label separated the cells by 0.35 and token kind took all but 0.07 of that back.*
