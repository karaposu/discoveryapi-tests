# Task 2 — Scope Drops and Logic Fixes (Decision Archaeology)

This file records the design decisions that led to the final Task 2 contract in `desc.md`. The `desc.md` describes the *final* state Task 2 commits to. This file describes *how we got there*: which paradigms were **dropped** from the active contract table and why, which paradigms were **lifted** to a different layer (e.g., from `ExpansionParameters` to `B2BQuerySpec`), and which logic-level restructurings (enum collapses, field liftings, LLM-to-Python migrations) reshape the original 9-paradigm design into the post-Task-2 form.

**Drop vs Lift — distinct verdicts:**
- **Dropped** means the paradigm no longer has runtime behavior. Its enum tag stays declared for backward compatibility, but no transformation it claimed to perform is actually executed.
- **Lifted** means the paradigm's runtime behavior is *preserved*, just moved to a different layer (typically because it's not properly per-combination). The transformation still happens; the location of the controlling field changes.

If `desc.md` answers *"what is Task 2?"*, this file answers *"why is Task 2 shaped this way?"*.

---

## Why this scope (decision rationale)

- The codebase already implements no-preanalysis. Task 2 makes that **intentional** by writing it down, not accidental.
- Sensemaking (`devdocs/sensemaking/paradigms-preanalysis-requirements.md`) showed that within B2B scope the defaults are adequate for all 9 paradigms. The acute degradation cases (4 paradigms) all have B2B-sensible defaults in the current combinations.
- **The contract table contains transformations, not metadata.** This is the principle that surfaced during scoping and that drives the drops below. A paradigm that claims behavior its enum tag promises but no code/prompt actually consumes is a source of confusion, not of structure. Task 2 enforces this discipline.
- After collapsing `source_lane_targeting` to Python and simplifying `noise_control`, `query_syntax_shaping` turned out to be entirely subsumed by other paradigms. Task 2 drops it from the contract table to keep the spec honest about what each paradigm actually contributes.
- `field_and_evidence_targeting` turned out to be pure metadata, not a transformation — its content (`target_fields`) was deterministically derivable from `entity_type`. Task 2 drops it from the contract table and derives `target_fields` via a small helper from `B2B_QUERY_SPEC.entity_type` (see the lift below).
- `tool_and_evidence_mode_targeting` was also metadata-only — its claimed behavior (SERP vs WSAPI vs dataset routing) requires retrieval paths the runner does not have. Task 2 drops it from the contract table.
- `discovery_flow` was also metadata-only — its claimed behavior (multi-step person-first vs company-first discovery) requires a multi-step pipeline the runner does not have. Task 2 drops it from the contract table under the same transformations-only principle.
- **`entity_targeting` was *lifted*, not dropped.** Its value (`person_profile` / `company_profile` / `mixed_person_company`) is properly query-scoped, not combination-scoped — every combination in a run is hunting the same kind of entity, determined by what the user query is asking for. Task 2 moves `entity_type` from `ExpansionParameters` to `B2BQuerySpec` (as a required field). The `target_fields_for(entity_type)` derivation still runs; its input now comes from `B2B_QUERY_SPEC.entity_type` instead of `combination.parameters.entity_type`. The active paradigm count after the 4 drops + 1 lift is **4 in the combination contract table, not 9**.
- Per-query constraint values (industry, geography, company_type, role_title_family, seniority_band, department_or_function, company_size_or_stage) were duplicated across every combination — a drift trap whenever `QUERY` changes. Task 2 lifts them into a single `B2B_QUERY_SPEC` object in `config.py` (Option 3 from the design discussion). Combinations no longer declare per-query values; they only declare combination-specific dials. The drift trap is structurally eliminated. `entity_type` was lifted into the same object (see above).
- Adding a preanalysis layer doubles the architectural surface (two LLM call types instead of one) and only pays off if we have data showing the default-application is insufficient. We don't have that data yet. Task 2 produces it.
- Until we have the no-preanalysis baseline measured, any preanalysis work is speculative.

---

## Dropped paradigms

Four of the original 9 paradigms in `expansion_paradigm_types.py:ExpansionParadigm` are dropped from the Task 2 active contract table. The enum tags themselves stay declared (no enum-value removal — that would be a broader refactor); only the paradigm rows in the contract table are dropped.

A fifth paradigm (`entity_targeting`) is **lifted** rather than dropped — see "Lifted paradigm: `entity_targeting`" below. After both the drops and the lift, the active contract table has 4 paradigms (down from the original 9).

### Dropped paradigm: `query_syntax_shaping`

After collapsing `source_lane_targeting` to Python and simplifying `noise_control`, every value of `syntax_strategy` is subsumed by another paradigm:

| `syntax_strategy` value | Who actually does the work | Status |
|---|---|---|
| `site_operator` | `source_lane_targeting` (Python `SOURCE_LANE_TO_PREFIX`) | redundant |
| `negative_terms` | `noise_control` (LLM picks ≤2 categories) | redundant |
| `quoted_phrase` | `constraint_handling` (preservation already quotes multi-word industry/geography) | redundant |
| `exact_title` | `constraint_handling` (preservation already quotes the title) | redundant |
| `boolean_or` | `intent_and_terminology` (this IS title broadening with synonyms) | redundant |
| `natural_language` | the *absence* of the above; expressible as "don't broaden the title" | redundant |

`query_syntax_shaping` therefore does no work that another paradigm doesn't already do. Task 2 drops it from the contract table.

**The one bit of information it uniquely carried** — "broaden the title with OR alternatives, yes or no" — is preserved by replacing `parameters.syntax_strategy` with a single boolean `parameters.broaden_title` (default `False`). When `broaden_title=True`, `intent_and_terminology` produces OR-grouped title alternatives in the rendered query. When `broaden_title=False`, the title is rendered verbatim (single quoted phrase). This is the only behavioral signal from the old `syntax_strategy`; everything else was duplication.

**What stays in code:**
- The `ExpansionParadigm.query_syntax_shaping` enum value (the *paradigm tag*) is left in the enum for backward compatibility with old reports and to avoid a broader refactor. Task 2 just stops treating it as an active paradigm.

**What changes in code:**
- `ExpansionQuerySyntaxStrategy` (both the paradigm-types and schemas copies): NOT changed in Task 2. The 6-value enum stays declared, but `parameters.syntax_strategy` is no longer read by the rendering prompt or by any Python code. It becomes vestigial like `exclusion_strength`.
- `ExpansionParameters.broaden_title: bool = False`: NEW field added. This is the one structural addition Task 2 permits beyond the source_lane collapse, justified by the fact that without it the post-Task-2 model loses the only distinction `syntax_strategy` could express.
- The rendering prompt drops the entire `syntax_strategy is the dominant mechanic of the query` section.

**What the rendering LLM is told about title broadening:**
- A short instruction tied to `broaden_title`: *if `broaden_title=True`, broaden the title with 2-3 OR-grouped synonyms inside parentheses, e.g. `("VP Sales" OR "Head of Sales" OR "CRO")`. Otherwise render the title as a single quoted phrase.*

### Dropped paradigm: `field_and_evidence_targeting`

`field_and_evidence_targeting` was supposed to "bias the expansion toward sources likely to expose fields from the B2B contact-data contract." In practice it did nothing of the kind:

| Where `target_fields` shows up | What actually happens |
|---|---|
| Declared on every combination as `_PERSON_TARGET_FIELDS` / `_COMPANY_TARGET_FIELDS` / their union | Just copied; never used to shape anything |
| Serialized into `ExpansionOutputItem.target_fields` for the report | Recorded but not consulted downstream |
| `COMBINATION_SYSTEM_PROMPT` references | None. The prompt does not mention `target_fields`. The rendering LLM is given the list as part of the combination JSON but has no rule telling it to bias the query toward those fields. |
| Judge prompt references | None. The judge infers expected fields from `original_query`; it never reads `target_fields`. |

So the paradigm was metadata-only AND its content was deterministically derivable from `entity_type`:

| `entity_type` | derived `target_fields` |
|---|---|
| `person_profile` | `_PERSON_TARGET_FIELDS` |
| `company_profile` | `_COMPANY_TARGET_FIELDS` |
| `mixed_person_company` | union of both |

Every combination today already followed this mapping. The paradigm was `entity_type` re-expressed as a list of strings — pure duplication.

**Task 2 drops it from the contract table.** `target_fields` is no longer declared on individual combinations; it is derived by a helper that reads `entity_type` from `B2B_QUERY_SPEC` (per the `entity_targeting` lift below).

**What stays in code:**
- The `ExpansionParadigm.field_and_evidence_targeting` enum value (the *paradigm tag*) stays in the paradigm enum for backward compatibility with old reports. Task 2 just stops treating it as an active paradigm.
- `ExpansionParameters.target_fields` stays declared on the model (Task 2 is not a refactor) but combinations no longer set it explicitly. It becomes vestigial when set on a combination; the derivation overrides it.

**What changes in code:**
- The constants `_PERSON_TARGET_FIELDS` and `_COMPANY_TARGET_FIELDS` move from being per-combination assignments to being the data source for the derivation. They stay in `experiment.py` (or move to a small helper module) — but are no longer typed into every combination row.
- A small helper `target_fields_for(entity_type)` is added (single function, ~5 lines). `build_expansion_output_item()` calls it to populate `ExpansionOutputItem.target_fields`, passing `B2B_QUERY_SPEC.entity_type` (not a per-combination value — see the `entity_targeting` lift below).
- Every combination in `EXPANSION_COMBINATIONS` STOPS declaring `target_fields`. The field is filled in by the helper at item construction time.
- `COMBINATION_SYSTEM_PROMPT` — already had no reference to `target_fields`, so no prompt change is needed for the drop itself.

**Net effect.** One more N→1 reduction in duplicated source code: instead of every combination repeating `target_fields=_PERSON_TARGET_FIELDS` (or its company variant), the mapping lives in one helper. Same structural improvement as `B2B_QUERY_SPEC` for per-query values and `SOURCE_LANE_TO_PREFIX` for site: operators.

### Dropped paradigm: `tool_and_evidence_mode_targeting`

`tool_and_evidence_mode_targeting` was supposed to "shape the expansion for the kind of downstream evidence expected" — SERP vs WSAPI vs dataset lookup. It does none of that, because the runner only has one retrieval path:

| Where `expected_evidence_mode` shows up | What actually happens |
|---|---|
| Declared on every combination (`snippet_only`, `content`, or `structured_enrichment`) | Set once when authoring the combination |
| Serialized into `ExpansionOutputItem.expected_evidence_mode` for the report | Recorded but not consulted downstream |
| `COMBINATION_SYSTEM_PROMPT` references | None. The prompt does not mention `expected_evidence_mode`. The rendering LLM has the value in the combination JSON but no rule telling it to shape the query based on it. |
| Retrieval branching | None. `BrightDataGoogleSERPRetrievalClient.search_sync()` runs unconditionally. There is no `if expected_evidence_mode == 'structured_enrichment': use_wsapi(...)` anywhere. |
| Judge branching | None. The judge sees `original_query`, `candidate_result`, `returned_evidence` — not `expected_evidence_mode`. |

So this paradigm is **metadata-only**, applied under the transformations-only principle. It is also the *weakest* of the dropped paradigms because:

- The two ostensible non-default values (`content`, `structured_enrichment`) would require retrieval paths (full-page content fetcher, WSAPI route) that **do not exist in the runner**.
- Even if those paths existed, the choice is a *retrieval configuration*, not an *expansion paradigm*. It would belong next to the retrieval client, not in `EXPANSION_COMBINATIONS`.

**Task 2 drops it from the contract table.**

**What stays in code:**
- The `ExpansionParadigm.tool_and_evidence_mode_targeting` enum value (the *paradigm tag*) stays declared in the paradigm enum for backward compatibility.
- `ExpansionParameters.expected_evidence_mode` stays declared on the model (Task 2 is not a refactor). It becomes vestigial — set on combinations, recorded in the report, ignored by all Python and by the rendering prompt.

**What changes in code:**
- Nothing imperative. The combinations may continue to set `expected_evidence_mode` for traceability, but no code path consumes the value. If a combination's author wants to omit it, fine; if they want to keep `snippet_only` for everything, also fine. The field is documented as vestigial.
- `COMBINATION_SYSTEM_PROMPT` — already has no reference to `expected_evidence_mode`, so no prompt change is required.

**Net effect.** Removes a misleading row from the contract table that claimed to control the retrieval path while controlling nothing. Reduces the active paradigm count from 7 → 6 (which the subsequent `discovery_flow` drop + `entity_targeting` lift further reduce to **4 active**).

### Dropped paradigm: `discovery_flow`

`discovery_flow` was supposed to control the discovery path (person-first vs company-first vs mixed). Under no-preanalysis mode with single-query SERP retrieval, it does nothing:

| Where `discovery_flow` shows up | What actually happens |
|---|---|
| Declared on every combination (`person_first` / `company_first` / `company_then_person` / `mixed`) | Set once when authoring the combination |
| Serialized into `ExpansionOutputItem.discovery_flow` for the report | Recorded but not consulted downstream |
| `COMBINATION_SYSTEM_PROMPT` references | None. The prompt does not mention `discovery_flow`. The rendering LLM has the value in the combination JSON but no rule telling it to alter the query based on it. |
| Multi-step pipeline branching | None. The runner executes one SERP per combination. There is no "find companies first, then look inside them for people" sequence in `experiment.py`. The whole concept of a multi-step flow doesn't exist. |
| Judge branching | None. |

Applied under the transformations-only principle: `discovery_flow` is metadata-only. It would only be meaningful if the runner supported multi-step discovery (find companies, then for each company find people inside it), which it does not. Its current presence in the contract table is purely aspirational.

**Task 2 drops it from the contract table.**

**What stays in code:**
- The `ExpansionParadigm.discovery_flow` enum value (the paradigm tag) stays declared in the paradigm enum for backward compatibility.
- `ExpansionParameters.discovery_flow` stays declared on the model. It becomes vestigial — set on combinations, recorded in the report, ignored by all Python and by the rendering prompt.
- `ExpansionOutputDiscoveryFlow` (the schemas mirror) stays declared.

**What changes in code:**
- Nothing imperative. Combinations may continue to set `discovery_flow` for traceability, but no code path consumes the value. `COMBINATION_SYSTEM_PROMPT` already has no reference to it, so no prompt change is required.

**Net effect.** Active paradigm count drops from 6 → **5**. The subsequent `entity_targeting` *lift* (see next section) reduces it further to **4 active in the contract table**.

---

## Lifted paradigms

A paradigm is **lifted** (not dropped) when its runtime behavior is preserved but moves to a different layer of the system. The transformation still happens; the controlling field is just elsewhere.

### Lifted paradigm: `entity_targeting`

`entity_targeting` was an active paradigm in earlier Task 2 drafts: every combination declared an `entity_type` value (`person_profile` / `company_profile` / `mixed_person_company`), which fed the `target_fields_for(entity_type)` derivation that populated `ExpansionOutputItem.target_fields`.

The problem: **`entity_type` is properly query-scoped, not combination-scoped.** Look at any concrete query:

| Natural query | What it's about | What every combination should hunt |
|---|---|---|
| "VP Sales or Head of Sales at US cybersecurity SaaS startups" | A person | `person_profile` |
| "Chief Revenue Officers at B2B fintech companies in New York" | A person | `person_profile` |
| "Cybersecurity SaaS startups in the United States" | A company | `company_profile` |
| "VPs of Engineering and the companies that employ them" | Both | `mixed_person_company` |

The entity type is determined by the user's natural-language query, not by which combination is testing it. There is no sensible run where one combination has `entity_type=person_profile` while another combination on the same query has `entity_type=company_profile` — the second combination would just be hunting the wrong shape.

Per-combination duplication of `entity_type` was the same drift trap as the other lifted fields (industry, geography, …):

| Where `entity_type` appeared (pre-lift) | What actually happened |
|---|---|
| `ExpansionParameters.entity_type` on every combination row | Same value typed into every row; if `QUERY` changes person→company, every combination row must be updated |
| Serialized into `ExpansionOutputItem.entity_type` for the report | Recorded per record, but the value was always the same across records in a run |
| Input to `target_fields_for(entity_type)` derivation | The derivation runs the same way regardless of which combination is calling it, because the input is constant |

So Task 2 lifts `entity_type` to `B2B_QUERY_SPEC` (as a required field), parallel to `industry`, `geography`, `role_title_family`, and the other query-scoped values lifted in the "Query spec specification" section of `desc.md`.

**Drop vs Lift — this is a lift, not a drop:**
- The `target_fields_for(entity_type)` derivation still runs.
- Every report still has `target_fields` populated.
- The judge still gets the right behavior on question 2 (`matches_requested_entity_type`) because the natural query is still the judge's input.

The only thing that changes is **where the controlling field lives**: `ExpansionParameters` → `B2BQuerySpec`. The paradigm's enum tag (`ExpansionParadigm.entity_targeting`) stays declared in the paradigm enum, consistent with how dropped paradigms keep their tags.

**What stays in code:**
- The `ExpansionParadigm.entity_targeting` enum value stays in the paradigm enum for backward compatibility.
- `B2BQuerySpec.entity_type` (required field) is the new controlling location.
- The `target_fields_for(entity_type)` derivation in `experiment.py` stays, but now reads `entity_type` from `B2B_QUERY_SPEC`.

**What changes in code:**
- `ExpansionParameters.entity_type` is REMOVED. It's an 8th field removed from `ExpansionParameters` alongside the 7 other query-scoped values (industry, geography, role_title_family, seniority_band, department_or_function, company_type, company_size_or_stage).
- `B2BQuerySpec` gains `entity_type: ExpansionParameterEntityType` as a required field (not `Optional`, unlike the other 7 query-scoped fields, because `target_fields_for()` always needs a value).
- `EXPANSION_COMBINATIONS` rows no longer declare `entity_type`.
- `build_expansion_output_item()` reads `B2B_QUERY_SPEC.entity_type` and passes it to `target_fields_for()` when populating `ExpansionOutputItem.target_fields`.
- `ExpansionOutputItem.entity_type` itself: still set on the output item for traceability, sourced from `B2B_QUERY_SPEC.entity_type`. Every record in a single run has the same `entity_type` value (because every record came from the same `B2B_QUERY_SPEC`).

**Net effect.** Reduces the active paradigm count in the combination contract table from 5 → **4**. Eliminates one more piece of per-combination duplication. The transformation `entity_targeting` was contributing to (driving the `target_fields_for()` derivation) is preserved — just controlled from the query layer instead of the combination layer.

**Why a lift instead of a drop:** the dropped paradigms (`query_syntax_shaping`, `field_and_evidence_targeting`, `tool_and_evidence_mode_targeting`, `discovery_flow`) all had behavior that was either redundant with other paradigms or aspirational-without-a-runner-feature. `entity_targeting`'s behavior (driving `target_fields`) is real and runs in every Task 2 run. The structural mistake was placing the controlling field on `ExpansionParameters` instead of on `B2BQuerySpec`. The lift fixes the placement without removing the behavior.
