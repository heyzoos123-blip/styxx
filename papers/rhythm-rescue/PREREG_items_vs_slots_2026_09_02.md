# PREREG — what does rotation buy: items, or slots? The clamp's loss scored twice on the same predictions — 2026-09-02

Fathom Lab · 2026-09-02 · rhythm-rescue · **FROZEN before confirmatory data.** Runner:
`run_items_vs_slots.py` (imports `run_rhythm_rescue` and `run_untied_control`; trains the parent's
three arms on the parent's task with nothing changed; adds a second score and a seeded evaluation).

## Where this came from, disclosed

A draft contrasted the parent's ORDERED copy task with a SORTED twin. Three referees reviewed it
and all three said amend; the judge that would have consolidated them was unavailable, so the
author did, and abandoned the SORTED contrast on the confounds referee's objection: every
permutation-invariant target of these inputs is a function of the multiset, which a single
theta = 0 integrator subspace holds linearly in every arm, so a SORTED task never loads the
recurrence and its gap is set by readout and initialization, not by the bank. It is also
information-poor by construction (13.6 against 21.5 bits at K = 6) and prior-predictable
(input-blind accuracy 0.40 per position at K = 20). The gaming referee's zero-task-selection
control is promoted to the test: score the ORDERED arms' own predictions a second way. The
chance-corrected thresholds below were proposed by that referee and **re-derived by the author**
by Monte Carlo before freezing (200,000 draws per K, numpy seed 0); the runner re-derives them
again as a plumbing gate.

## The question

If phase is an order code, the clamped bank should still *hold* the items it was shown and lose
only where they go. ITEMS is the multiset overlap between the K predicted symbols and the K true
ones, divided by K; a perfectly shuffled recall scores 1.0 on ITEMS and 1/12 on ORDER. Capacity on
each score is first-failure on the parent's grid: the largest K such that every grid point up to
it clears its bar. For ORDER the bar is the parent's 0.80 at every K (the anchors are unchanged;
on both committed receipts first-failure and largest-passing-K agree for every arm and seed, and
the runner asserts it). For ITEMS the bar is chance-corrected to the same level:
lambda = (0.80 - 1/12)/(1 - 1/12) = 0.78182 and thr_item[K] = base[K] + lambda (1 - base[K]),
with base the input-blind bag baseline: {1: 0.0836, 2: 0.1596, 3: 0.2298, 4: 0.294, 6: 0.4063,
8: 0.5015, 10: 0.5813, 12: 0.6482, 15: 0.655, 18: 0.6772, 20: 0.6969}.

Every arm is scored on identical trials: the evaluation draw is seeded per (K, seed), 2048
trials, so the parent's confound of scoring arms on whatever the training RNG left behind is
gone. Three arms, three seeds, 4000 steps, D = 256 — the parent's settings.

## Predictions, before data

Order code: CLAMPED's ITEMS capacity sits within one grid step of FREE's while its ORDER capacity
sits 3.33 items below — items retained, slots lost. Capacity: CLAMPED loses items too. A third
outcome the reviews forced the design to name: FREE retains *fewer* items than CLAMPED, which
would mean retained rotation is a nuisance for content, and is not an order-code result.

## Gates

```gates
{"gates": {"G_P_anchors": {"metric": "anchor_max_abs_dev", "op": "<=", "value": 1.5,
                           "power_basis": "FREE, CLAMPED and REAL2 re-run on the ORDERED score must land within 1.5 items of the committed seed-mean capacities (6.0, 2.6667, 2.6667: rhythm_rescue_result.json#/gate and untied_control_result.json#/arms); the untied control met this at 0.0 on this CPU"},
           "G_P_rule": {"metric": "rule_mismatch", "op": "<=", "value": 0,
                        "power_basis": "first-failure capacity must equal the parent's largest-passing-K capacity on the ORDER score for every arm and seed, as it does on every committed receipt; a mismatch means the anchors changed meaning"},
           "G_P_baseline": {"metric": "baseline_max_abs_dev", "op": "<=", "value": 0.002,
                            "power_basis": "the runner re-derives the input-blind bag baseline by the same Monte Carlo; a deviation over 0.002 at 200,000 draws means the frozen table is not what the code computes"},
           "G_C_gap": {"metric": "gap_order", "op": ">=", "value": 2.0,
                       "power_basis": "the parent's ORDER gap is 3.3333 on two devices; under 2 the effect this contrast decomposes did not reproduce"},
           "G_PC_items": {"metric": "free_items", "op": ">=", "value": 6.0,
                          "power_basis": "positive control: FREE must retain items at least as far as it retains order (6.0); an item score that floors below the order capacity of the arm that has order is not a measurement of retention"},
           "G_CEIL": {"metric": "free_items_max", "op": "<=", "value": 18,
                      "power_basis": "K = 20 is the top of the grid and of the training range; a seed at 20 has an item capacity the grid cannot bound, so a small item gap against a pinned FREE is a bound, not a number; 18 is the last grid point with room above it"},
           "G_ITEM_free_not_worse": {"metric": "gap_items", "op": ">=", "value": -1.0,
                                     "power_basis": "FREE contains CLAMPED as its theta = 0 special case; FREE more than one seed-step below CLAMPED on items means rotation as initialised (theta ~ U(0, pi/2)) hurt retention, a different finding from an order code"},
           "G_ITEM_gap_small": {"metric": "gap_items", "op": "<=", "value": 1.0,
                                "power_basis": "one item is one seed one grid step at the 4..12 spacing, or one seed one step at 12..20; two seeds one step (1.33) is a real item gap; the bar the parent used for its rescue rule, tightened by one"},
           "G_SLOTS": {"metric": "interaction", "op": ">=", "value": 2.0,
                       "power_basis": "the ORDER gap must exceed the ITEMS gap by at least 2 items, the arc's floor for a real effect and the grid's step above K = 4; with the parent's gap of 3.33 and an item gap under 1 this is one grid step of headroom, disclosed as such"}},
 "outcomes": [{"when": {"G_P_anchors": false}, "verdict": "INVALID__plumbing_anchors_drifted"},
              {"when": {"G_P_rule": false}, "verdict": "INVALID__plumbing_kcap_rule"},
              {"when": {"G_P_baseline": false}, "verdict": "INVALID__plumbing_baseline_drifted"},
              {"when": {"G_C_gap": false}, "verdict": "INVALID__gap_did_not_reproduce"},
              {"when": {"G_PC_items": false}, "verdict": "INVALID__item_score_floored"},
              {"when": {"G_ITEM_free_not_worse": false}, "verdict": "ROTATION_NUISANCE__free_retains_fewer_items"},
              {"when": {"G_CEIL": false, "G_ITEM_gap_small": true}, "verdict": "ITEMS_RETAINED_SLOTS_LOST__items_at_grid_ceiling"},
              {"when": {"G_CEIL": false, "G_ITEM_gap_small": false}, "verdict": "INVALID__item_ceiling_unreadable"},
              {"when": {"G_ITEM_gap_small": true, "G_SLOTS": true}, "verdict": "ITEMS_RETAINED_SLOTS_LOST"},
              {"when": {"G_ITEM_gap_small": true, "G_SLOTS": false}, "verdict": "PARTIAL__slots_lost_below_the_bar"},
              {"when": {"G_ITEM_gap_small": false}, "verdict": "ITEMS_LOST_TOO__capacity_not_slots"}],
 "smoke_verdict": "INVALID__smoke_plumbing_only"}
```

`real2_items_minus_clamped_items` and `free_minus_real2_order` are reported beside the gates
and gate nothing: whether the untied real bank retains more items than the tied one is the
diversity question on content, and this design does not bar it.

## What this does not test

Position decoding from the state, permuted MNIST, or any task the author chose: the only task is
the parent's. The item score is coarse at the grid's top (steps of 3 above K = 12) and the
interaction subtracts across resolutions; the bars are in items and say so. Three seeds.

Committed before the run. Smoke (`--smoke`: 200 steps, one seed, grid 1/2/4/8) is INVALID-only.
Result -> `items_vs_slots_result.json` -> `RESULT_items_vs_slots_2026_09_02.md`, sworn.
