# Which expansion paradigms can be applied directly, without a preanalysis LLM call?

## User Input

> what expansion paradigms doesnt require preanalysis llm call and directly can be apply?
>
> for example source_lane_targeting can be applied in generic way as site:linkedin and not like person company etc. for b2b this doesnt require a preanalysis llm call, but if preanalysis happens source_lane_targeting can produce more custom tailored options
>
> intent_and_terminology also doesnt require preanalyiss llm call
>
> what others doenst require ?

---

## SV1 — Baseline Understanding

The user wants a per-paradigm verdict on whether each of the 9 expansion paradigms (`intent_and_terminology`, `entity_targeting`, `discovery_flow`, `source_lane_targeting`, `constraint_handling`, `field_and_evidence_targeting`, `noise_control`, `query_syntax_shaping`, `tool_and_evidence_mode_targeting`) can be applied without a separate upfront "preanalysis" LLM call. They've named two as "doesn't require preanalysis" and want the same verdict for the other seven. The implicit goal: decide whether the proposed preanalysis call is optional or required, and which paradigms benefit from it most.

---

## Phase 1 — Cognitive Anchor Extraction

**Constraints**

- **C1** — There are 9 paradigms in `expansion_paradigm_types.py:ExpansionParadigm`. The set is fixed for this analysis.
- **C2** — The architecture in question has two LLM call types: **(A) preanalysis / classification** and **(B) expansion / rendering**. The question is about (A) specifically.
- **C3** — The user explicitly accepts a quality trade-off: paradigms can be applied "in a generic way" without preanalysis OR "more custom tailored" with preanalysis. So "doesn't require" does not mean "wouldn't benefit from."

**Key Insights**

- **KI1** — "Doesn't require preanalysis" is overloaded. The user's two examples occupy **different mechanisms**: `source_lane_targeting` works with a *generic heuristic default* (`site:linkedin` alone), while `intent_and_terminology` works because the expansion LLM does the semantic work *inline*. Same verdict, different reason.
- **KI2** — The real axis is not binary. There are at least three distinct application modes: (a) pure heuristic with a fixed default, (b) needs an LLM but only at expansion time, (c) genuinely depends on preanalysis output.
- **KI3** — All 9 paradigms can technically be applied without preanalysis, but with different fallback modes and different degrees of quality loss.
- **KI4** — Two of the 9 paradigms are *declarative flags*, not query transformations (`entity_targeting`, `discovery_flow`). For them, "apply without preanalysis" means "accept a fixed default value."

**Structural Points**

- **SP1** — Two-layer architecture: preanalysis → expansion. Each paradigm has a different relationship to each layer.
- **SP2** — Three dimensions matter per paradigm: (i) does it need ANY LLM call?, (ii) does it specifically need preanalysis?, (iii) what does it lose without preanalysis?
- **SP3** — Quality is a continuum: every paradigm can degrade to a generic version. Preanalysis is what enables query-specific tailoring.

**Foundational Principles**

- **FP1** — Preanalysis is an upfront, query-specific classification call producing atoms (entity type, source lanes, alternative wordings, …). Its output feeds combination selection.
- **FP2** — Expansion is a per-combination LLM/heuristic operation rendering one concrete query string.
- **FP3** — A paradigm *requires* preanalysis only if its application logic depends on query-specific knowledge that can ONLY come from preanalysis. If a sensible default or expansion-time semantic call suffices, preanalysis is OPTIONAL.

**Meaning-Nodes**

- **MN1** — "Preanalysis" = the upfront query-classification LLM call.
- **MN2** — "Apply directly" = produce a usable transformation without that upfront call.
- **MN3** — "Generic application" = uses defaults, query-agnostic.
- **MN4** — "Tailored application" = uses query-specific atoms from preanalysis.

### SV2 — Anchor-Informed Understanding

The question is multi-dimensional even though it reads as binary. The "doesn't require preanalysis" frame conflates at least two distinct cases: paradigms that are pure heuristics with a sensible fixed default (source_lane_targeting), and paradigms that need LLM at expansion time but don't need a separate preanalysis call (intent_and_terminology). The answer needs at minimum a three-tier classification, not a yes/no.

---

## Phase 2 — Perspective Checking

**Technical / Logical**

Each paradigm operates at a different abstraction level. Some are pure string manipulation (`query_syntax_shaping`), some need semantic understanding (`intent_and_terminology`), some are declarations (`entity_targeting`). Without preanalysis, the expansion LLM is doing classification + rendering in one call — it has the original query and the combination spec, so it can infer entity type, broaden synonyms, etc. inline. But each render does the work *redundantly* and possibly *inconsistently* across combinations.

→ **KI5** — Skipping preanalysis doesn't eliminate the classification work; it duplicates it across N expansion calls and risks cross-combination inconsistency.

**Human / User**

The user is iterating toward a final experiment design and is implicitly cost-conscious. They've established earlier in the conversation that heuristic factors are preferred where possible. So "doesn't require preanalysis" is a *desirable* verdict, not a neutral one.

→ **KI6** — The user is looking for permission to drop preanalysis on as many paradigms as possible. The answer should be honest about quality loss, not just yes/no.

**Strategic / Long-term**

Without preanalysis, the system is query-agnostic only if every paradigm can sensibly default. For B2B-specific queries the defaults work; for non-B2B queries they fail silently.

→ **KI7** — "Can be applied without preanalysis *for B2B*" ≠ "Can be applied without preanalysis universally." The user's question implicitly assumes B2B framing.

**Risk / Failure**

- Wrong defaults: `entity_targeting=person_profile` when the query is actually about companies → wrong `source_lane` → wrong SERP.
- LLM-inline-classification inconsistency: each expansion call might reach a slightly different classification from the same query, producing incoherent combinations.

→ **KI8** — Skipping preanalysis trades 1 upfront LLM call for *downstream consistency risk* + *default-mismatch risk*.

**Resource / Feasibility**

Preanalysis cost = 1 LLM call per run. Without preanalysis, expansion calls need bigger prompts (must include enough context to classify inline) and likely produce inconsistent results. The net cost of dropping preanalysis is small but not zero.

**Definitional / Internal Consistency**

"Apply" needs to be defined. If "apply source_lane_targeting" means "produce a useful source-restricted query," then bare `site:linkedin.com` (no `/in` or `/company`) is borderline — it's barely targeting. If "apply" means "produce any query with a `site:` operator," generic counts. The user's example endorses generic, so generic application counts here.

**Definitional / Frame-exit Completeness**

Gating check: the inquiry inherits one multi-value term that warrants Existence Enumeration — **"preanalysis"** itself.

- *Existence Enumeration on "preanalysis":* could refer to (i) a strict classification call returning structured atoms, (ii) any upfront LLM call (e.g., one shared synonym-generation call that isn't strictly classification), (iii) static system-prompt context baked in at build time.
- *Role Assessment:* the user's framing seems to mean (i) specifically. But (ii) might also satisfy the user's underlying need (quality tailoring) at lower cost; (iii) is a degenerate case that doesn't really count as "preanalysis."
- *Verdict Rigor:* a clean "doesn't require preanalysis" verdict for paradigms that work fine without (i) might survive only because we never tested whether they need (ii). For paradigms in the expansion-LLM-only category, the practical replacement *is* something like (ii).

→ **KI9** — The answer depends on whether "preanalysis" means strict classification or any upfront LLM work. Defaulting to (i).

**Phase / Calibration-State**

The project is in an early-design state. The matrix hasn't been empirically validated. The "with vs without preanalysis" trade-off depends on quality data we don't have yet. So the answer should **categorize the options**, not prescribe one.

### SV3 — Multi-Perspective Understanding

The categorization needs at least three modes (pure heuristic, expansion-LLM-only, preanalysis-dependent), but no paradigm strictly *requires* preanalysis — all 9 can be applied without it, with degraded quality. The real distinction is between paradigms where the degradation is acceptable (defaults are fine) versus paradigms where it can be acutely wrong (default may not match the query). The project's B2B framing hides this — the defaults happen to work well for B2B specifically. For a query-agnostic system, the defaults would fail more often.

---

## Phase 3 — Ambiguity Collapse

### Ambiguity 1 — What does "doesn't require preanalysis" actually mean?

**Strongest counter-interpretation:** It means "needs no LLM call at all" (pure heuristic). Under this reading, `intent_and_terminology` DOES require preanalysis because it needs an LLM to generate synonyms.

**Why the counter fails (structural grounds):** The user explicitly names `intent_and_terminology` as "doesn't require preanalysis," but that paradigm is the most clearly semantic one in the 9. If the counter-interpretation were correct, the user contradicts themselves. The non-contradictory reading is: "preanalysis" specifically refers to the upfront classification call, not all LLM use. An LLM call at expansion time is fine.

**Confidence:** HIGH (the user's own examples force this interpretation).

**Resolution:** "Doesn't require preanalysis" = "can be applied without a separate upfront classification LLM call." The paradigm may still use LLM at expansion time.

**What is now fixed:**
- Three application modes: (i) pure heuristic, (ii) needs LLM at expansion time only, (iii) needs preanalysis.
- "Apply" includes generic-default application.

**What is no longer allowed:** Treating "doesn't require preanalysis" as identical to "purely heuristic."

**What depends on this:** The classification table for the 9 paradigms.

**What changed in the model:** Two LLM call types are now first-class — the answer separates "preanalysis use" from "expansion-time LLM use."

### Ambiguity 2 — Are declarative flags ("entity_targeting", "discovery_flow") paradigms that can be "applied"?

**Strongest counter-interpretation:** They're not transformations — you don't "apply" them. They're tags. Asking whether they require preanalysis is a category error.

**Why the counter fails:** The project enumerates them as paradigms in the same enum. They have downstream effect — combination selection uses them. They're applied in the sense that they're SET to a value, and that value shapes other paradigms (e.g., `entity_type=person_profile` biases `source_lane` selection toward person sources).

**Confidence:** HIGH.

**Resolution:** Flags count as "applied" when they're SET. The question becomes: can we set a sensible default without preanalysis? Usually yes, but the default may not match the query.

### Ambiguity 3 — Does "applying generically" actually count as applying the paradigm?

**Strongest counter-interpretation:** `source_lane_targeting` with bare `site:linkedin.com` (no `/in` or `/company`) barely targets anything. Counting that as "applied" inflates the paradigm's effective coverage.

**Why the counter fails:** The user's own example endorses this as a valid mode. Generic `site:linkedin.com` is still narrower than no `site:` operator at all, so the paradigm is having SOME effect.

**Confidence:** HIGH (per user framing).

**Resolution:** Generic application counts. The classification reflects what's *possible*, not what's *optimal*.

### Load-bearing concept test — "preanalysis"

**Counter-interpretation:** "Preanalysis" might be a loop-coined neologism. The codebase currently has only `request_expansion_for_combination` — no separate preanalysis function exists. The concept is being treated as if it's already implemented.

**Why the counter fails:** The user is explicitly asking a *design question* about a hypothetical preanalysis layer. The whole conversation context establishes preanalysis as a *proposed* upfront classification call. So "doesn't require preanalysis" really means "doesn't need us to add this proposed layer."

**Resolution:** Honor the user's framing — preanalysis = the proposed upfront classification call. The answer evaluates each paradigm against that hypothesis.

### Specific-vs-pattern recognition cue

The user offered 2 specific examples (`source_lane_targeting`, `intent_and_terminology`). The wider pattern is 9 paradigms with varied mechanisms. The risk is concluding that the 2 examples are representative when they actually exemplify **different mechanisms** (heuristic-with-default vs expansion-LLM-only). The answer must surface this — extending the pattern naively would miss the structural variety.

### SV4 — Clarified Understanding

The question's "doesn't require preanalysis" has been narrowed to: "can be applied without a separate upfront classification LLM call." Three implementation modes are distinguishable: pure heuristic (no LLM at all), expansion-LLM-only (LLM at render time but not preanalysis), and preanalysis-dependent. The user's two examples occupy the first two modes — and no paradigm strictly falls into the third under this definition. So the honest answer is: ALL 9 paradigms can be applied without preanalysis; the substantive question is HOW they degrade without it.

---

## Phase 4 — Degrees-of-Freedom Reduction

**Fixed:**
- Three-mode taxonomy: pure heuristic / expansion-LLM-only / preanalysis-dependent.
- "Apply" includes generic-default mode and flag-setting.
- Output format: per-paradigm table with mode, fallback, and quality loss.

**Eliminated:**
- Binary yes/no answer.
- Treating the user's two examples as the only cases (they're actually two different modes).
- Implying preanalysis is required for any paradigm.

**Viable:**
- A 9-row table classifying each paradigm by mode and quality loss without preanalysis.
- An explicit note that the B2B framing makes the defaults look adequate; non-B2B queries would degrade more.
- Honest open-flagging of empirical questions we can't answer without running experiments.

### SV5 — Constrained Understanding

The answer is a table over the 9 paradigms with columns: (1) how it's applied without preanalysis, (2) what kind of work is required (heuristic / expansion-LLM / flag-default), (3) what's lost without preanalysis (quality degradation, not capability loss). Plus an explicit note that no paradigm strictly REQUIRES preanalysis under this definition — all 9 can ship without it.

---

## Phase 5 — Conceptual Stabilization

### The full per-paradigm table

| Paradigm | Application mode without preanalysis | Work type | What's lost without preanalysis |
|---|---|---|---|
| `source_lane_targeting` | Generic `site:linkedin.com` or other fixed default | Heuristic | Person-vs-company precision (`/in` vs `/company`); per-query source selection |
| `noise_control` | Append fixed negative-term list | Heuristic | Adaptation to query-specific noise sources |
| `query_syntax_shaping` | Apply quotes, OR, site:, -term mechanically | Heuristic | Nothing significant — syntax is universal |
| `constraint_handling` (preservation half) | Pass constraints through verbatim | Heuristic | Nothing — preservation is mechanical |
| `field_and_evidence_targeting` | Default field set (e.g., all B2B fields) | Heuristic | Field selection narrowed to what the specific query needs |
| `tool_and_evidence_mode_targeting` | Default to SERP-shaped queries | Heuristic | Routing to WSAPI / dataset when query is better served that way |
| `intent_and_terminology` | Expansion-LLM generates synonyms inline from query text | Expansion-time LLM | Cross-combination consistency of the synonym set |
| `constraint_handling` (broadening half) | Expansion-LLM identifies and broadens constraints inline | Expansion-time LLM | Same — consistency across combinations |
| `entity_targeting` | Default value (e.g., `person_profile`) | Flag default | Correctness when the query is actually about companies |
| `discovery_flow` | Default value (e.g., `person_first`) | Flag default | Mostly nothing — not used by single-query SERP today |

### The three application modes, by group

- **Pure heuristic (no LLM anywhere) — 6 entries:**
  `source_lane_targeting` (generic mode), `noise_control`, `query_syntax_shaping`, `field_and_evidence_targeting` (default-set mode), `tool_and_evidence_mode_targeting` (SERP-default mode), and the preservation half of `constraint_handling`.

- **Expansion-LLM-only (no preanalysis, LLM at render time) — 2 entries:**
  `intent_and_terminology`, and the broadening half of `constraint_handling`.

- **Flag-default (just pick a value) — 2 entries:**
  `entity_targeting`, `discovery_flow`.

**Total paradigms requiring preanalysis strictly: 0.**

### What preanalysis actually buys (so the trade-off is honest)

Quality gain from preanalysis, ranked:

- **Big gain** — `entity_targeting`, `source_lane_targeting`, `intent_and_terminology`, `field_and_evidence_targeting`. Query classification meaningfully changes the right answer for these.
- **Moderate gain** — `constraint_handling`, `discovery_flow`, `tool_and_evidence_mode_targeting`. Useful but not transformative.
- **Little or no gain** — `noise_control`, `query_syntax_shaping`. Defaults are already query-agnostic.

### Important caveat — the B2B framing hides degradation risk

The defaults work because the project is scoped to B2B contact data. The default `source_lane=linkedin`, default `entity_type=person_profile`, default `exclusions=[jobs, hiring, …]` all happen to be sensible for B2B. For a non-B2B query (e.g., "best DSLR cameras under $1000"), these defaults are flat-out wrong. So "doesn't require preanalysis" is true *within the current project scope* but becomes false if the system is generalized to arbitrary queries.

### Open ambiguities (flagged, not resolved)

- **OPEN** — Whether the expansion-LLM-only mode introduces enough cross-combination inconsistency to justify preanalysis. Needs empirical data — multiple runs of the same query, with and without preanalysis, compared on consistency of inferred atoms.
- **OPEN** — Whether some narrower upfront LLM call (e.g., a synonym-only "atoms" call that isn't full classification) is a better trade-off than full preanalysis vs no preanalysis.

### SV6 — Final Stabilized Model

**No expansion paradigm strictly requires preanalysis.** All 9 can be applied directly, in one of three modes: pure heuristic (6 paradigms, counting half of `constraint_handling`), expansion-LLM-only (2 paradigms / 1.5 counting the other half of `constraint_handling`), or flag-default (2 paradigms). Preanalysis is a **quality lever, not a hard dependency** — it gives query-tailored answers where default-application gives generic answers. The cost of skipping preanalysis is **uneven quality loss**, acute for some paradigms (entity, source_lane, intent_and_terminology, field_and_evidence) and negligible for others (noise_control, query_syntax_shaping). Within the project's B2B framing the defaults are adequate; outside that framing they fail more.

### Difference from SV1

- SV1 expected a binary yes/no split. SV6 has three modes.
- SV1 implied preanalysis is required for some paradigms. SV6 finds it's never strictly required — only sometimes quality-improving.
- SV1 didn't distinguish "no LLM at all" from "no preanalysis specifically." SV6 makes that the core split (it's the structural difference between the user's two examples).
- SV6 surfaces a degradation risk SV1 didn't see: the B2B framing makes defaults look universally adequate; outside that frame they degrade noticeably for 4 of the 9 paradigms.
