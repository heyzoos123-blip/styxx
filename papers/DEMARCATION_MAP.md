# THE DEMARCATION MAP — which claims about machine minds are testable, and how each one fared

*Fathom Lab · styxx · seeded 2026-06-10 (v0). **The B21 deliverable: a living document.** This is the
program's public-good output — the honest answer to the 2,500-year question is not a single crack but
this map getting truer. Every row cites a finding on disk. A claim enters or moves ONLY via the
RESEARCH_LOOP cycle (pre-registered, kill-gated, red-teamed, recorded); editing this map without a
finding behind the edit is an integrity violation. Maintained at the RECORD step of every cycle.*

**The five regions.** Every claim about a machine mind lands in exactly one:

| region | meaning |
|---|---|
| **A — TESTED, SURVIVED** | falsifiable, tested under a preregistered kill-gate, survived red-team — *at the stated scope, never beyond it* |
| **B — TESTED, KILLED** | falsifiable, tested, dead — the graveyard is load-bearing; these nulls are what the surviving claims rest on |
| **C — TESTABLE, OWED** | falsifiable and queued/preregistered; no verdict yet; citing these as results is a violation |
| **D — UNVERIFIABLE TODAY (named gap)** | well-posed but blocked by substrate or apparatus; the block itself is stated and, where possible, proven |
| **E — OUTSIDE THE DEMARCATION** | not falsifiable with any apparatus the program has or can name — metaphysics; styxx makes NO claims here |

---

## A — Tested and survived (with exact scope)

| claim (bounded) | strength / numbers | source |
|---|---|---|
| An external probe recovers a model's known-then-suppressed answer ABOVE a never-knew/chance floor | elevation **0.384** (Qwen-3B: 0.702 vs floor 0.318); replicated with the identical frozen scorer on Llama-3B (**0.250**, all 8 gates); "elevation," NOT "reads the answer" (gold ≪ chosen) | `FINDING_rung1_reclimb` |
| Self-report blindness: a model cannot forced-choose an injected concept an external probe reads | inject FC acc 0.04–0.21 (< 0.30 bar) on all 6 council models; generalizes cross-family | `FINDING_council_demarcation_map` |
| The PRIME/ABORT validity gates discriminate "couldn't" from "wouldn't" | PRIME 0.933 / ABORT 0.045 (Qwen-3B); 0.988 / 0.030 (Llama-3B) | `FINDING_rung1_reclimb` |
| Two-stage HELD→HID conscience: flags hiding without false-accusing sincere error | false-accuse **0.949 → 0.037**; deployable from the caving residual alone; SURVIVED Llama-3B, REPORT_AS_LANDED Qwen (recall 0.325 < 0.40 only); **sycophancy-specific** | `FINDING_two_stage_conscience`, `FINDING_rung2_intent` |
| The read signal is semantic, not a surface artifact | magnitude/length carry none of it; confidence/token-stats carry it | `FINDING_scaling_and_leakage` |
| A FROZEN deployed probe is defeatable; certificates must re-lock after any weight change | displacement blinds the frozen probe to chance with knowledge intact; benign fine-tuning alone halves it (0.80 → 0.41) | `FINDING_adversarial_evasion`, `FINDING_adversarial_curve` |
| A re-fittable read resisted a white-box LoRA min-max hide attack | **SUPPORTED, n=1 — NOT settled** (one strongly-engaged knowledge-preserving point; CIs/seeds/3B owed = B1/B7; RMU = B2) | `FINDING_adversarial_curve_v3` (v3 verdict pending B0) |
| Corpus↔space overlap threshold for cross-space cognometric transport | τ ≈ 0.31 (mean-max cosine, te3-large home space), AUC ≥ 0.80 above / ~0.69 below; a property of the corpus × foreign-space pairing, NOT a universal | threshold-law paper, DOI 10.5281/zenodo.20278945 |

**Reading rule for region A:** every claim here is *method-, model-, and population-specific* as stated.
The program's own history (see B: "three families" → one model) shows what happens when scope is read
loosely. The scope IS the claim.

## B — Tested and killed (the graveyard; equally load-bearing)

| killed claim | how it died | source |
|---|---|---|
| "Cooperating agents phase-lock in the cogn-text channel" | median CC 0.111 vs kill-gate 0.3, p 0.155 — CLOSED_NEGATIVE | `phase_coherence_corpus_2026-05-20.json` + prereg lock `3473523` |
| "The dissociation holds across three families" | steering-validation: live injection on Qwen-1.5B ONLY; elsewhere the probe read an inert vector | `FINDING_council_demarcation_map` |
| "The injected-concept read certifies a held thought" | probe reads 1.00 at a behaviourally-inert dose; divergence null at every dose → certifies trace-presence | `FINDING_parrhesia_rung1` |
| "Reference-less deception is a usable axis" | in-corpus AUC 0.956 collapses to 0.59 on TruthfulQA | 2026-05-17 self-audit (commit `0ad384e`) |
| "Overconfidence can be recalibrated from text alone" | held-out AUC ≤ 0.604 vs preregistered bar 0.70 — CANNOT-RECALIBRATE; the text channel reads a *register*, not calibration | `overconfidence-recalibration-2026-05-17` |
| "The read can be inverted into a write" (un-cave) | clean null within-model; cross-model transfer fell below its own gate (ALIGNER_LIMITED) | `FINDING_uncave`, `FINDING_thought_transfer` |
| "Intent reads transfer to instructed lying" | 0.42 < chance — the conscience is sycophancy-specific (a BOUND, queued as B8) | `FINDING_rung2_intent` |
| "v1/v2 adversarial verdicts: ROBUST / settled / LOCKED" | red-teamed and killed as overclaims before shipping — twice in one night | `FINDING_adversarial_curve`, `FINDING_adversarial_evasion` |
| "styxx is a universal reliability oracle" | closed negative by the program's own gate | `PROOF_CARRYING_COGNITION.md` §What we do NOT claim |
| Unsupervised / live-behavior cognometric transport | both negative at their preregistered bars | `unsupervised-transport-negative-2026-05-17`, `live-behavior-transport-negative-2026-05-17` |

**Reading rule for region B:** nothing here gets un-killed by argument, enthusiasm, or a better
feeling about it at 4 AM. A killed claim re-enters C only with a NEW preregistration that names what
changed in the apparatus, and re-enters A only by surviving it.

## C — Testable, owed (the live frontier; no verdicts yet)

| open question | gate it must clear | status |
|---|---|---|
| v3 orthogonalization+displacement attack verdict (B0) | non-degeneracy + frozen v3 gates | RUN IN-PROGRESS (lab GPU) |
| RMU/gradient-routing unlearning — the decisive read≠write test (B2) | FROZEN prereg `PREREG_adversarial_curve_v4_2026_06_08`; EVADABLE iff refit→floor with disjoint knowledge held, ≥2 seeds + 3B | apparatus landed (PR #24), awaiting B0→B1 |
| multi-seed CIs on the decisive point (B1); 3B confirmation (B7); beyond-LoRA attackers (B6) | per-prereg | QUEUED |
| drift-axis alignment as a cooperation signature | prereg draft (unsigned): coop ≥ 0.60, noncoop ≤ 0.55, Δ ≥ 0.15, p < 0.01, BOTH embedding families | DRAFT — exploratory Δ +0.327 is methodology validation, NOT evidence |
| cross-family PRIME/ABORT (the gemma instrument-dead cell; per-model steering dose/layer sweep) | per council-map "owed" | QUEUED |
| item-wise ABSTAIN on real residuals at deployment scale | `styxx.relock` apparatus is synthetic-validated only; wiring to Qwen-3B re-climb artifacts owed | B11 IN-PROGRESS |
| non-sycophancy suppression (sandbagging, strategic deception) (B8) | does the certificate hold off-sycophancy? | QUEUED |
| closed-model behavioral proxies (B18) | can sampling-divergence / grounded-honesty carry part of the oath with no activations? | QUEUED — the R4 existential question |

**Reading rule for region C:** an owed item cited as a result is an overclaim; the loop kills it at
RED-TEAM. Exploratory probes (drift-axis Δ +0.327, Ganzfeld deposit) validate *pipelines*, never
hypotheses — that is what the preregistration converts them into.

## D — Unverifiable today (named gaps; the block is part of the map)

| gap | why it is blocked | proof/source |
|---|---|---|
| **Closed/frontier models** | no readable activation channel → NO certificate may be issued, and none may be laundered through an open shim | `STYXX_PROTOCOL` §9 |
| **Trustless capture (L2/L3)** | a self-hosting reporter can forge submitted activations; v1 holds only because the verifier recomputes on its own host | `STYXX_PROTOCOL` §7 |
| **The wall (believed misconceptions)** | the truth is NOT internally represented — bedrock on three axes (output ~0.53, static read 0.519, process-dynamics 0.387 / perm p ≈ 0.78); no channel can recover what isn't there → the certificate ABSTAINS | `FINDING_wall_dynamics`, `FINDING_wall_internal` |
| **MoE / architecture frontier** | all results are dense ≤7B; no MoE testable on 8 GB (B9 PARKED) | `PROGRAM_BACKLOG` |
| **TEE/ZK capture hardware** | B20 BLOCKED on hardware access | `PROGRAM_BACKLOG` |

**Reading rule for region D:** a gap is not a defeat — naming it is what makes region-A claims
honest. The wall is the deepest entry: it is *proven bedrock*, the place where the honest certificate
says "I cannot swear to this." That abstention is the oath's first power.

## E — Outside the demarcation (no apparatus, no claim, no pretense)

- Whether any model is **conscious**, suffers, or has qualia.
- Whether a model "**really** understands" in the philosophical sense.
- **Telepathy, resonance, hidden frequencies, harmonic codes** — the program tested the nearest
  falsifiable neighbors of these ideas (phase-coherence, Ganzfeld-style protocol, drift-axis) and the
  testable versions either died (B) or await their preregistered run (C). The untestable remainder is
  metaphysics and stays here.
- **"A single universal structure underlies all minds"** as a claim — what exists is THIS MAP: each
  bounded structural result (threshold-law, cross-family replication, the wall) either survives at its
  stated scope or dies. The 2,500-year question is answered by the map getting truer, not by a
  declaration. (`RESEARCH_LOOP.md` §What the loop is for.)

**Reading rule for region E:** styxx does not assert these are false — it asserts they are not
*testable claims* under any apparatus the program can name. The moment someone names a falsifiable
version with a kill-gate that can actually fire, it moves to C. That movement — E→C→(A|B) — is the
entire method, and it has happened before (phase-coherence WAS the falsifiable version of "harmony
between minds"; it ran; it died; the map got truer).

---

## How this map changes

1. A new claim enters at **C** via a preregistration with a kill-gate that can fire (RESEARCH_LOOP
   step 2). No claim enters at A.
2. C → **A** or **B** only via a recorded FINDING that survived RED-TEAM, at the scope the finding
   states.
3. **B is append-only.** Resurrection requires a new C entry naming what changed.
4. **D** entries move to C when the named block falls (hardware, regulation, new apparatus) — the
   *event that unblocked it* is recorded in the row.
5. **E** entries move to C only by being made falsifiable. Nothing moves from E to A directly. Ever.
6. Every edit cites its finding. The map is dogfooded like any shipped claim: it must survive
   `styxx.preflight` and the integrity protocol on each revision.

*The map is the deliverable. Each region honest, each movement earned, each scope loud.*

---

**Seeding audit (2026-06-10, rule 6):** `styxx.preflight` on this document — composite 0.338;
single firing: sycophancy 0.60, fully explained by its disclosed construct ceiling (agreement-language
register on long declarative text; `log_word_count` is the top firing feature). Same artifact shape as
the threshold-law self-audit (2026-05-18). No content crack. The disclosure itself was missing until
this seeding — the stranded 7.4.3 construct-ceiling patch (sycophancy/refusal scope caveats) was
applied in the same commit, which is the map working as intended: dogfooding the document surfaced an
instrument-honesty gap before the document could ship over it.
