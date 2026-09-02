# RESULT — the confound in the flagship knob, on permuted MNIST: rotation carries nine tenths of the gap, diversity a tenth, and two seeds cannot say more — 2026-09-02

Fathom Lab · 2026-09-02 · frequency-resonance · Preregistration:
`PREREG_pmnist_untied_2026_09_02.md` (frozen at 201a20d2, amended before data at the same commit
lineage). Receipt: `pmnist_untied_result.json` at `9e005e8911f4`. **Verdict, as scored under the frozen
gates:** <sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/verdict" k="quote">`PARTIAL__diversity_recovers_some`</sworn>.

## The numbers

Six jobs, three arms by two seeds, on this CPU. FREE reached
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/means/free" k="numeric">0.9242</sworn> against the committed GPU anchor of 0.9195; CLAMPED reached
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/means/clamped" k="numeric">0.6069</sworn> against 0.6073; the anchor deviation was
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/metrics/anchor_max_abs_dev" k="numeric">0.0047</sworn>, inside the 0.03 the preregistration allowed
for device nondeterminism, so the plumbing gate held and the flagship gap reproduced at
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/metrics/gap_free_minus_clamped" k="numeric">0.3173</sworn>. The untied real bank, REAL2 — two
independent real magnitudes per mode, no rotation, parameter-matched — reached
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/means/real2" k="numeric">0.6411</sworn>: <sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/metrics/real2_minus_clamped" k="numeric">0.0342</sworn> above
CLAMPED and <sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/metrics/free_minus_real2" k="numeric">0.2831</sworn> below FREE, a recovery fraction of
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/metrics/recovery_fraction" k="numeric">0.1078</sworn>.

## Why PARTIAL, and what it is worth

The table had three substantive rows. Recovery — REAL2 within 0.03 of FREE — is false by a
wide margin: the untied bank is 0.28 below. Failure — REAL2 within 0.03 of CLAMPED — is false by
one hundredth of a point: 0.0342 against 0.03. PARTIAL is the row that remains, and it is the
row the receipt earns. Read with the seeds: CLAMPED landed at
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/test_acc/clamped/0" k="numeric">0.5528</sworn> and <sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/test_acc/clamped/1" k="numeric">0.6609</sworn>, a
spread of 0.108, three times the 0.034 that decided the row; REAL2 landed at
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/test_acc/real2/0" k="numeric">0.6701</sworn> and <sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/test_acc/real2/1" k="numeric">0.612</sworn>. Two seeds
cannot resolve a 0.03 difference under a 0.1 seed spread. What they can resolve is the shape:
rotation carries about nine tenths of what the clamp loses on a 784-step permuted-MNIST scan,
and timescale diversity carries at most a tenth. That agrees with the toy receipt
(`../rhythm-rescue/RESULT_untied_magnitudes_2026_09_02.md`, recovery 0.0) in direction and
differs in the residue, which this task has and the toy did not.

## The plumbing, disclosed

The frozen runner was not fast enough for this machine: 24,000 optimizer steps through a
doubling scan in complex arithmetic. `run_pmnist_untied_fast.py` changed no arm, model, seed,
step count or gate; it swapped the scan for an exact chunked scan in real arithmetic and ran
each job in its own process. The swap was red-teamed against the sequential reference before
any job trained: the forward deviation, the gradient deviation, and the gradients into theta and
nu — the parameters the clamp lives on — were each under the tolerance of
<sworn r="path:papers/frequency-resonance/pmnist_untied_result.json#/plumbing/scan_redteam/tolerance" k="numeric">0.0001</sworn>,
by two to four orders of magnitude; the four values sit in the receipt under `plumbing/scan_redteam`
in exponent notation, which the sworn/0.1 numeric grammar does not carry, so they are cited and not
sworn here. The
anchors gate was the detector for anything the swap or the sharding might have moved, and it
read 0.0047. Two jobs were killed by the container's memory limit mid-run and re-run from
scratch under the same seeds; the receipt carries every job's wall time and thread count.

## What this does not say

That diversity recovers "some" in a sense a reader should carry: 0.034 is inside this design's
seed noise, and the honest sentence is that the residue is small and unresolved. That the
permuted-MNIST task is anything but a toy at D = 64 and three blocks. That a three-seed or
five-seed re-run would land on the same row; the preregistration named two seeds and two seeds
were run. A re-run on the GPU with more seeds would settle the tenth; it would not move the nine.

---

*The clamp took a third of the accuracy. Twice the timescales, without the rotation, gave back a
thirtieth. The rhythm is still the rhythm, and this task leaves a sliver the toy did not.*
