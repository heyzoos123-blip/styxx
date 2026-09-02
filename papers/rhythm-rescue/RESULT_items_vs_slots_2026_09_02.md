# RESULT — items or slots: the clamp loses the items too. Rotation buys memory here, not order — 2026-09-02

Fathom Lab · 2026-09-02 · rhythm-rescue · Preregistration: `PREREG_items_vs_slots_2026_09_02.md`
(frozen at c51d8bdf). Receipt: `items_vs_slots_result.json` at `7d047c4da55c`. **Verdict, as scored
under the frozen gates:** <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/verdict" k="quote">`ITEMS_LOST_TOO__capacity_not_slots`</sworn>.

## The numbers

The parent's three arms, trained on the parent's copy task with nothing changed, scored twice on
the same predictions. By ORDER — the parent's score — capacities landed exactly on the committed
anchors: FREE <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/free/kcap_order_mean" k="numeric">6.0</sworn>, CLAMPED
<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/clamped/kcap_order_mean" k="numeric">2.6667</sworn>, REAL2
<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/real2/kcap_order_mean" k="numeric">2.6667</sworn>; anchor deviation
<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/metrics/anchor_max_abs_dev" k="numeric">0.0</sworn>, the first-failure rule agreed with the parent's
rule on every arm and seed (<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/metrics/rule_mismatch" k="numeric">0</sworn> mismatches), and the frozen
bag baseline re-derived within <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/metrics/baseline_max_abs_dev" k="numeric">0.0007</sworn>. By ITEMS —
multiset overlap, chance-corrected per K to the order bar's level — the capacities were the same
numbers: FREE <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/free/kcap_items_mean" k="numeric">6.0</sworn>, CLAMPED
<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/clamped/kcap_items_mean" k="numeric">2.6667</sworn>, REAL2
<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/real2/kcap_items_mean" k="numeric">2.6667</sworn>. Seed by seed, FREE held six items on both
scores three times; CLAMPED held three, three and two on both; REAL2 held three, three and two on
both. The order gap is <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/metrics/gap_order" k="numeric">3.3333</sworn> and the item gap is
<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/metrics/gap_items" k="numeric">3.3333</sworn>; their difference, the interaction the order-code
hypothesis predicted would be about three items, is <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/metrics/interaction" k="numeric">0.0</sworn>.

## The reading

The candidate this preregistration tested — phase as a slot code, so that a clamped bank keeps
what it was shown and loses only where — is refuted on this task at this scale. At K = 6 the
clamped bank's shuffled-recall score is <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/clamped/seeds/0/items/6" k="numeric">0.7309</sworn>
against FREE's <sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/arms/free/seeds/0/items/6" k="numeric">0.9243</sworn> on seed 0: it is not holding
the six symbols in the wrong order; it is holding fewer of them. Read with the arc's two other
receipts — untied real magnitudes recover 0.0 of the clamp's loss on this toy and about a tenth
of it on permuted MNIST — the rotation is load-bearing for holding information at all, not for
ordering it, and the "order code" was the author's guess, now the third reading today that the
receipts overruled. What rotation *is* doing remains open; two candidates the reviews raised and
this design did not test are interference (rotation keeps items in different phases from
colliding on a shared magnitude) and effective dimensionality of the state.

## Plumbing, disclosed

Evaluation draws were seeded per (K, seed) so all three arms scored identical 2048-trial sets,
removing the parent's confound of scoring on whatever the training RNG left. The chance-corrected
item thresholds were proposed by a referee and re-derived by the author before freezing; the
runner re-derives them again as a gate. Nine gates, eleven outcomes, every gate combination
mapped once, checked by enumeration before the run. Nine trainings on this CPU in under ten
minutes.

## What this does not say

That rotation buys nothing about order anywhere: a task where items are held and slots lost may
exist and was not chosen, by design. That the result holds beyond D = 256, K <= 20, three seeds,
and a linear recurrent bank. That REAL2's equality with CLAMPED on items
(<sworn r="path:papers/rhythm-rescue/items_vs_slots_result.json#/metrics/real2_items_minus_clamped_items" k="numeric">0.0</sworn>) is a measurement of diversity on
content: it is reported, and it gates nothing.

---

*Asked whether the clamped bank remembers what and forgets where, the receipt said it forgets
what. The rhythm is memory before it is order.*
