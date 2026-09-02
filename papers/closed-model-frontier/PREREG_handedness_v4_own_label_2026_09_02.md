# PREREG — token-level h, v4: the author's OWN label, operationalized — 2026-09-02

Fathom Lab · 2026-09-02 · closed-model-frontier · **FROZEN before scoring.** Runner:
`handedness_accusations_v4.py`. A re-split of the same 349 joined rows of
`handedness_v3_result.json`; no token is re-judged, no panel is re-run.

## Why v4 exists

Two referees read v3 on 2026-09-02. The statistical one showed the header/line gap is mostly
token kind (kind-adjusted 0.117 against raw 0.3124; `handedness_v3_stratified.json`). The
definitional one showed v3's "header-handed" cell never operationalized the thesis it was read
as supporting: `header_bound` is *any trigger anywhere in the header row and none on the line*,
bag-of-words at table scope. Six of the eight header-cell false accusations are rank indices
whose own column label is `Rank`; the trigger lived in another column. And 32 line-cell rows are
table rows whose trigger is the author's own row label, "structural" by the thesis's definition
and "incidental" by v3's code. The thesis says *a label the author chose and committed to*. This
preregistration tests that, as written, on the receipts that exist.

## The operationalization, frozen

For every joined row in v3's `header` or `line` cell (334 rows; range-sanity rows excluded, they
report under v0.14), read the token's line from the hash-verified corpus at its pinned sha.

- If the line is a markdown table data row (`styxx.certify._table_rows`, the verifier's own
  definition): find the token's cell by counting `|` before the ledger's `col`; the **own column
  label** is the header cell at that index; the **row label** is the first cell of the data row.
  **STRUCTURAL** iff `_TRIGGERS` (the verifier's own vocabulary, imported) matches the own
  column label or the row label. Otherwise **INCIDENTAL**.
- If the line is not a table row: **INCIDENTAL.** A prose `Accuracy: 0.95` is co-occurrence
  under this operationalization; v4 does not test the colon-label form and says so.

Genuine = the 2026-08-27 panel's `CLAIM` on that row, unchanged from v3. "Largest repository" =
the repository with the most rows among the 334 (`hopit-ai/Moda`, 184).

## Disclosed prior — strong, and contaminated twice

The definitional referee's re-split was read before this was written: header 157/165 = 0.9515;
line-table 27/32 = 0.8438; line-prose 81/137 = 0.5912. Under the own-label rule the structural
cell should be near 0.93 and the incidental cell near 0.6, so `G_T` is expected to pass on the
raw difference. The statistical referee's objection was read too: the author expects `G_K`, the
kind-adjusted gate, to be the one that fails, because decimals are near ceiling in every cell.
The bars are frozen with that expectation on the record, and the verdict that follows from
`G_T` true and `G_K` false is named below so it cannot be read as a win.

## Gates

```gates
{"gates": {"G_P_docs": {"metric": "docs_missing", "op": "<=", "value": 0,
                        "power_basis": "every joined row's document must load from the cache hash-verified at its pinned sha; a missing document is plumbing, not evidence"},
           "G_P_eight": {"metric": "eight_named_rows_not_incidental", "op": "<=", "value": 0,
                         "power_basis": "the definition, not the panel, must put v3's eight header-cell false accusations (T0224 T0229 T0234 T0239 T0244 T0249, the Rank column; T0141 T0181, config values in a row-label column) in INCIDENTAL; if the code disagrees with the stated definition, the run is plumbing-INVALID"},
           "G_P_rowlabel": {"metric": "line_table_rows_reclassified_structural", "op": ">=", "value": 20,
                            "power_basis": "the referee counted 32 line-cell table rows; the definition must move at least 20 of them to STRUCTURAL or it is not the definition stated"},
           "G_N_cells": {"metric": "min_cell_n_ex_top_repo", "op": ">=", "value": 20,
                         "power_basis": "v3's own floor (G_N_cells 20), applied after dropping the largest repository so one model card cannot carry the verdict; v3's header cell was 72% one repository"},
           "G_T_own_label": {"metric": "delta_ex_top_repo", "op": ">=", "value": 0.15,
                             "power_basis": "v3's bar for the raw difference, now applied to the cells the thesis actually names and with the largest repository dropped"},
           "G_K_kind": {"metric": "kind_adjusted_delta_all", "op": ">=", "value": 0.15,
                        "power_basis": "the same bar, Mantel-Haenszel-weighted across decimal/integer/comma strata over all repositories: the structure reading must survive token kind, which v3's did not (0.117)"}},
 "outcomes": [{"when": {"G_P_docs": false}, "verdict": "INVALID__corpus_not_rebuilt"},
              {"when": {"G_P_docs": true, "G_P_eight": false}, "verdict": "INVALID__operationalization_failed_plumbing"},
              {"when": {"G_P_docs": true, "G_P_eight": true, "G_P_rowlabel": false}, "verdict": "INVALID__operationalization_failed_plumbing"},
              {"when": {"G_P_docs": true, "G_P_eight": true, "G_P_rowlabel": true, "G_N_cells": false}, "verdict": "INVALID__cells_too_thin_ex_top_repo"},
              {"when": {"G_P_docs": true, "G_P_eight": true, "G_P_rowlabel": true, "G_N_cells": true, "G_T_own_label": true, "G_K_kind": true}, "verdict": "OWN_LABEL_ACCUSES_TRUER__against_kind"},
              {"when": {"G_P_docs": true, "G_P_eight": true, "G_P_rowlabel": true, "G_N_cells": true, "G_T_own_label": true, "G_K_kind": false}, "verdict": "OWN_LABEL__form_confounded"},
              {"when": {"G_P_docs": true, "G_P_eight": true, "G_P_rowlabel": true, "G_N_cells": true, "G_T_own_label": false}, "verdict": "NOT_SEPARABLE_BY_OWN_LABEL"}],
 "smoke_verdict": "INVALID__smoke_plumbing_only"}
```

Reported beside the gates, gating nothing: the raw difference over all repositories, both cells'
shares with Wilson intervals, the per-kind cells, the table-versus-prose split the referee
found, and the eight named rows' cells.

## What v4 does not do

It does not re-judge a token: the panel is the 2026-08-27 panel, one model family, whose
sanity gate failed at 0.4933, and every share here inherits that. It does not test prose
labels. It does not touch `n=` (declared structural on zero panel data; the definitional
referee's objection to that label stands and is answered in the mapping, not here). A verdict
here licenses nothing about the accusing branch; that is `PREREG_S1`'s alone.

Committed before scoring. Result -> `handedness_v4_result.json` ->
`RESULT_handedness_v4_*_2026_09_02.md`, sworn.
