# Task 2 — No-Preanalysis Expansion Benchmark

## Purpose

Lock in the **two-phase, no-classification-preanalysis** operating mode for the expansion benchmark and define exactly what that means in code and in the experimental design. Earlier sensemaking work (`devdocs/sensemaking/paradigms-preanalysis-requirements.md`) established that no expansion paradigm strictly requires a classification preanalysis call. Task 2 commits to a clean split:

- **Phase A (LLM):** one upfront semantic-expansion call per run, producing a fixed set of query variants seeded by LLM-based paradigms.
- **Phase B (Python):** deterministic decoration of those variants with heuristic paradigms (`source_lane_targeting`, `noise_control`).

This eliminates cross-combination LLM variance — the single biggest noise source in the previous design — and cleanly separates semantic work (LLM) from syntactic work (Python).

This task is **not** about evaluating whether *full* preanalysis (classification, runtime intent inference, query routing) is the right long-term choice. It commits only to atom-style variant generation as the single up-front LLM call.

---

## What we are doing

We are finalizing the expansion-benchmark runner under three rules:

1. **One LLM call for semantic expansion**, executed once per run, producing N query variants. This is *atom/variant generation*, not classification — the LLM is not deciding which combinations to test, what category the query belongs to, or which heuristics to apply. It is producing semantically-broadened query bodies that the runner consumes.
2. **Zero LLM calls during per-combination rendering.** Each combination's final query is composed by deterministic Python from (a) one of the N variants and (b) a heuristic decoration choice.
3. **One LLM call per top-N SERP candidate for boolean judging** (unchanged from the existing runner).

The result is a **two-phase pipeline**:

```
Phase A (LLM, ONCE per run):
  B2B_QUERY_SPEC → N query variants tagged with paradigm seeds

Phase B (Python, deterministic, MANY per run):
  for each variant V × heuristic combination H:
    final_query = decorate(V, H)
    SERP(final_query) → judge top-N

Total LLM calls per run = 1 (variant generation) + N × |H| × JUDGE_TOP_N (judging)
```

`B2B_QUERY_SPEC` (including `entity_type`) is consumed at Phase A and again as context at Phase B; combinations themselves do not carry per-query content.

---

## How we plan to do it

### Architecture (two-phase flow per run)

```
config.py                              (knobs + B2B_QUERY_SPEC)
   │
   ▼
experiment.py: run()
   │
   ├── Phase A — generate semantic variants
   │     │
   │     └── request_query_variants(B2B_QUERY_SPEC, llm_paradigm_seeds)
   │             ↳ ONE LLM call
   │             ↳ returns List[QueryVariant]  (N entries, e.g. 8)
   │
   ├── For each variant V in the result:
   │     For each (source_lane L, noise_control N) heuristic combination:
   │       │
   │       ├── final_query = compose(V.query_body, L, N)
   │       │       ↳ Pure Python: site:prefix + body + negatives
   │       │
   │       ├── BrightDataGoogleSERPRetrievalClient.search_sync(final_query)
   │       │       ↳ RetrievedCandidate[]
   │       │
   │       └── For each top-N candidate:
   │             request_b2b_boolean_judge_output(candidate)
   │               ↳ 10 YES/NO answers
   │
   └── save_report(report) → outputs/b2b_<UTC>.json
```

There is **no per-combination LLM call**. The LLM produces variants once; Python composes the rest.

### Phase A — LLM expansion (one call per run)

**Input.** `B2B_QUERY_SPEC` (which includes `natural_query`, `entity_type`, and the structured constraint fields) plus the LLM paradigm seed list.

**LLM paradigm seeds** (these are the *semantic* paradigms — the LLM uses them as a menu of transformation styles):

- **`verbatim`** — produce the natural query unchanged. Acts as the no-broadening baseline.
- **`title_broadening`** — broaden the role/title terms in the query with synonyms (`"VP Sales"` → `("VP Sales" OR "Head of Sales" OR "CRO" OR "Head of Revenue")`).
- **`industry_broadening`** — broaden the industry/domain terms (`"cybersecurity SaaS"` → `("cybersecurity SaaS" OR "security software" OR "infosec platform")`).
- **`geography_broadening`** — broaden geography/location terms (`"United States"` → `("United States" OR "USA" OR "US")`).
- **`combined_broadening`** — broaden two or more of the above simultaneously.

**Output.** A list of `N` `QueryVariant` objects (typical N = 8, configurable).

**Variant schema:**

```python
class QueryVariant(BaseModel):
    """One LLM-produced query body, tagged with which seed paradigms shaped it."""
    variant_id: str                  # e.g., "var_001_verbatim"
    seeds: List[ExpansionParadigm]    # which seed paradigms shaped this variant
    query_body: str                  # the rendered query string (no site:, no negatives)
    rationale: str                   # one-sentence explanation
```

**What the LLM is responsible for:**
- Producing well-formed Google query bodies that preserve the constraints from `B2B_QUERY_SPEC` (industry, geography, seniority, role title family) — broadening them with synonyms when the seed calls for it.
- Properly quoting multi-word phrases.
- Properly using parenthesized OR groups for broadenings.
- Tagging each variant with which seeds it embodies.

**What the LLM is NOT responsible for:**
- Choosing a `source_lane` or `site:` operator. The query body has no site: prefix; Phase B prepends one.
- Choosing negative terms. The query body has no `-keyword` exclusions; Phase B appends them.
- Picking which heuristics get tested against the variant. That's the runner's job.

**Prompt structure** (`llm_request_logic.py:QUERY_VARIANTS_SYSTEM_PROMPT`):

```text
You generate semantic query expansions for B2B contact-data discovery.

Given a query spec and a list of paradigm seeds, produce N query variants.
Each variant:
- Preserves the spec's constraints (industry, geography, seniority, role title family).
- Is shaped by one or more of the listed seed paradigms.
- Uses Google syntax for any broadenings: ("A" OR "B" OR "C") with parentheses.
- Quotes multi-word phrases.
- Does NOT include site: operators.
- Does NOT include negative -keyword exclusions.

Tag each variant with the seeds that shaped it. One verbatim variant must be included.
```

### Phase B — Heuristic decoration (deterministic Python)

For each variant produced in Phase A, Python decorates it with combinations of two heuristic paradigms:

#### `source_lane_targeting` (Python, always applied)

Picks one of 8 values: `linkedin`, `crunchbase`, `theorg`, `cognism`, `uplead`, `kompass`, `signalhire`, or `None`.

Python prepends `SOURCE_LANE_TO_PREFIX[source_lane]` to the variant's `query_body`:

```python
SOURCE_LANE_TO_PREFIX = {
    "linkedin":   "site:linkedin.com",
    "crunchbase": "site:crunchbase.com",
    "theorg":     "site:theorg.com",
    "cognism":    "site:cognism.com",
    "uplead":     "site:uplead.com",
    "kompass":    "site:kompass.com",
    "signalhire": "site:signalhire.com",
    None:         "",                       # no site: restriction
}
```

#### `noise_control` (Python, optional toggle)

Two options per combination: `apply` or `skip`. When `apply`, Python appends a deterministic per-source negative-term list:

```python
NEGATIVES_FOR_SOURCE = {
    "linkedin":   ["-jobs", "-workday"],
    "crunchbase": ["-jobs"],
    "theorg":     ["-jobs"],
    "cognism":    ["-pricing", "-blog"],
    "uplead":     ["-pricing", "-blog"],
    "kompass":    ["-pricing"],
    "signalhire": ["-pricing", "-blog"],
    None:         ["-jobs", "-blog"],
}
```

Each source has at most 2 negatives. The mapping is hardcoded in Python — there is no LLM involvement at this step. (Previously the LLM picked the negatives per-combination; this caused variance and is replaced.)

#### Composition

```python
def compose_final_query(variant: QueryVariant, lane: Optional[B2BSourceLane], noise_control: bool) -> str:
    prefix = SOURCE_LANE_TO_PREFIX[lane]
    body = variant.query_body
    negatives = " ".join(NEGATIVES_FOR_SOURCE[lane]) if noise_control else ""
    return f"{prefix} {body} {negatives}".strip()
```

Pure Python. Reproducible. Same `(variant, lane, noise_control)` → same final query, every time.

### Combination model

A **combination** under the two-phase architecture is a 3-tuple:

```
combination = (variant_id, source_lane, noise_control)
```

- `variant_id` ∈ one of the N variants from Phase A (e.g., 8 variants)
- `source_lane` ∈ `{linkedin, crunchbase, theorg, cognism, uplead, kompass, signalhire, None}` (8 values)
- `noise_control` ∈ `{apply, skip}` (2 values)

**Total combinations per run** = `N × 8 × 2`.

For N = 8 variants, total = **128 combinations** (matching the previous design's full Cartesian, with cleaner attribution).

**There is no longer a "K policy" question.** The old design's omissible-paradigm subset is collapsed: title broadening and constraint broadening are now baked into specific variants by Phase A. The combination's choices are just (which variant, which source, whether to apply negatives).

Worked examples:

```text
combination = (var_001_verbatim, linkedin, apply)
  → "site:linkedin.com VP Sales or Head of Sales at US cybersecurity SaaS startups -jobs -workday"

combination = (var_002_title_broadened, linkedin, apply)
  → 'site:linkedin.com ("VP Sales" OR "Head of Sales" OR "CRO") "cybersecurity SaaS" "United States" -jobs -workday'

combination = (var_002_title_broadened, crunchbase, skip)
  → 'site:crunchbase.com ("VP Sales" OR "Head of Sales" OR "CRO") "cybersecurity SaaS" "United States"'

combination = (var_005_combined_broadening, None, apply)
  → '("VP Sales" OR "Head of Sales") ("cybersecurity SaaS" OR "security software") ("United States" OR "USA") -jobs -blog'
```

### Paradigm classification under Task 2

Of the original 9 paradigms in `expansion_paradigm_types.py:ExpansionParadigm`:

| Status | Paradigm | Phase / Location |
|---|---|---|
| **Active (Phase A — LLM seed)** | `intent_and_terminology` | Used as seed by Phase A's variant-generation call. The LLM applies it inline. Subsumes the old `constraint_handling (broadening)` half — both are "LLM broadens semantic terms in the query body". |
| **Active (Phase B — Python decorator)** | `source_lane_targeting` | Python prepends `site:` prefix from a fixed dict. |
| **Active (Phase B — Python decorator)** | `noise_control` | Python appends negative terms from a fixed `source_lane → negatives` dict. |
| **Lifted to `B2B_QUERY_SPEC`** | `entity_targeting` | `entity_type` is query-scoped, not combination-scoped. Drives the `target_fields_for(entity_type)` derivation. See `scope_drops_and_logic_fixes.md`. |
| **Subsumed by Phase A** | `constraint_handling` (preservation + broadening halves) | Phase A's LLM always preserves the spec's constraints in its variants; broadening happens when an LLM seed calls for it. Not a separate omissible toggle. |
| **Dropped** | `query_syntax_shaping` | See `scope_drops_and_logic_fixes.md`. |
| **Dropped** | `field_and_evidence_targeting` | See `scope_drops_and_logic_fixes.md`. |
| **Dropped** | `tool_and_evidence_mode_targeting` | See `scope_drops_and_logic_fixes.md`. |
| **Dropped** | `discovery_flow` | See `scope_drops_and_logic_fixes.md`. |

Net count: **3 active paradigms** (1 LLM seed in Phase A + 2 Python decorators in Phase B), **4 dropped**, **1 lifted to `B2B_QUERY_SPEC`**, **1 subsumed by Phase A** (`constraint_handling`).

### B2B query spec specification

Per-query content lives in a single `B2B_QUERY_SPEC` object in `config.py`. This is the human-authored structured form of the user query; it's consumed by Phase A as input and by Phase B as constraint context.

```python
# expansion_paradigm_types.py
class B2BQuerySpec(BaseModel):
    """Structured form of the user query. One instance per run.

    Holds every value that describes WHAT the run is searching for,
    independent of WHICH combination is being tested.
    """
    natural_query: str                                                       # required
    entity_type:             ExpansionParameterEntityType                    # required; person/company/mixed
    industry:                Optional[str] = None
    geography:               Optional[str] = None
    company_type:            Optional[str] = None
    company_size_or_stage:   Optional[str] = None
    role_title_family:       Optional[ExpansionParameterRoleTitleFamily]    = None
    seniority_band:          Optional[ExpansionParameterSeniorityBand]      = None
    department_or_function:  Optional[ExpansionParameterDepartmentOrFunction] = None
```

```python
# config.py
B2B_QUERY_SPEC = B2BQuerySpec(
    natural_query="VP Sales or Head of Sales at US cybersecurity SaaS startups in the United States",
    entity_type=ExpansionParameterEntityType.person_profile,
    industry="cybersecurity SaaS",
    geography="United States",
    company_type="startup",
    role_title_family=ExpansionParameterRoleTitleFamily.sales_leadership,
    seniority_band=ExpansionParameterSeniorityBand.vp,
    department_or_function=ExpansionParameterDepartmentOrFunction.sales,
)
QUERY = B2B_QUERY_SPEC.natural_query   # back-compat alias
```

`B2B_QUERY_SPEC` is consumed by Phase A (the LLM uses every field to shape its variants) and is recorded in the report. `entity_type` drives `target_fields_for(entity_type)` deterministically in Python.

The remaining hardcoded part is `B2B_QUERY_SPEC` itself — the human authors it once per run. Removing that last hardcoding requires real classification preanalysis, which is out of scope.

### Source lane specification

`source_lane` is a Phase B decorator. The combination picks one of 8 values; Python prepends the corresponding `site:` prefix.

| `source_lane` | Python prefix | Source character |
|---|---|---|
| `linkedin` | `site:linkedin.com` | Person + company profiles (high SERP value) |
| `crunchbase` | `site:crunchbase.com` | Company firmographics (high SERP value) |
| `theorg` | `site:theorg.com` | Org charts (high SERP value, free) |
| `cognism` | `site:cognism.com` | Paywalled lead database (mostly marketing in SERP) |
| `uplead` | `site:uplead.com` | Paywalled lead database (mostly marketing in SERP) |
| `kompass` | `site:kompass.com` | B2B company directory (partially indexable) |
| `signalhire` | `site:signalhire.com` | Contact database (mixed — paywalled details + indexable profile pages) |
| `None` | `""` (no prefix) | Unrestricted Google search |

The LLM never sees this mapping. Phase A produces variants without `site:` prefixes; Phase B adds the prefix.

### Noise control specification

`noise_control` is a Phase B decorator with deterministic per-source negatives.

```python
NEGATIVES_FOR_SOURCE = {
    "linkedin":   ["-jobs", "-workday"],
    "crunchbase": ["-jobs"],
    "theorg":     ["-jobs"],
    "cognism":    ["-pricing", "-blog"],
    "uplead":     ["-pricing", "-blog"],
    "kompass":    ["-pricing"],
    "signalhire": ["-pricing", "-blog"],
    None:         ["-jobs", "-blog"],
}
```

The combination's `noise_control` flag (apply / skip) determines whether these negatives are appended. The cap of ≤2 negatives per query is built into the dict (no entry has more than 2 terms).

The LLM never picks negatives. The previous design's LLM-picks-negatives behavior is replaced because it caused cross-combination variance.

### Code surface (what gets touched)

- `expansion_paradigm_types.py`:
  - **New type**: `B2BQuerySpec` (per "B2B query spec specification" above). 8 fields: `natural_query` (required), `entity_type` (required), 6 `Optional[…]` query-scoped fields.
  - **New type**: `QueryVariant` (per "Phase A" above). The LLM return shape.
  - **Type changes to `ExpansionParameters`**: REMOVES 8 query-scoped fields (the 7 lifted to `B2BQuerySpec` plus `entity_type`). Also removes per-combination `broaden_title` — not needed under the two-phase model, since broadening is selected by `variant_id` choice.
  - **Enum collapse**: `ExpansionParameterSourceLane` collapses from 6 values to 8 (`linkedin`, `crunchbase`, `theorg`, `cognism`, `uplead`, `kompass`, `signalhire`, `None`). Same for `ExpansionOutputSourceLane`. (Older B2B-paywalled exclusion-tagged lanes — `company_team_page`, `general_web` — are removed.)
  - **Vestigial**: `syntax_strategy`, `exclusion_strength`, `target_fields`, `expected_evidence_mode`, `discovery_flow` stay declared on `ExpansionParameters` for backward compatibility, but no Python code or prompt reads them.

- `config.py`:
  - Adds `B2B_QUERY_SPEC: B2BQuerySpec` constant. `QUERY` becomes a derived alias.
  - Adds `SOURCE_LANE_TO_PREFIX: dict[Optional[B2BSourceLane], str]`.
  - Adds `NEGATIVES_FOR_SOURCE: dict[Optional[B2BSourceLane], list[str]]`.
  - Adds `NUM_VARIANTS: int = 8` (or whatever default Phase A targets).
  - Optionally adds `LLM_PARADIGM_SEEDS: list[str]` listing which seeds Phase A uses (defaults to all five: verbatim, title_broadening, industry_broadening, geography_broadening, combined_broadening).

- `experiment.py`:
  - `run()` is restructured into the two-phase flow.
  - Removes per-combination LLM rendering. Adds one upfront Phase A call to `request_query_variants(B2B_QUERY_SPEC, seeds)`.
  - Adds `compose_final_query(variant, source_lane, noise_control) -> str` — pure Python composition.
  - Adds `target_fields_for(entity_type)` helper (unchanged from earlier spec; reads from `B2B_QUERY_SPEC.entity_type`).
  - `EXPANSION_COMBINATIONS` is no longer a hand-written list. The combinations are *generated* by iterating `variants × source_lanes × noise_control_options`. The generator is in `experiment.py`.
  - `build_expansion_output_item()` populates `ExpansionOutputItem` from `(variant, source_lane, noise_control)`. `target_fields` populated via `target_fields_for(B2B_QUERY_SPEC.entity_type)`.

- `llm_request_logic.py`:
  - Adds `request_query_variants(query_spec, seeds, num_variants) -> List[QueryVariant]`. New system prompt `QUERY_VARIANTS_SYSTEM_PROMPT` per "Phase A" above.
  - **Removes** `request_expansion_for_combination()` and the per-combination rendering path. Removes `COMBINATION_SYSTEM_PROMPT` entirely (no longer needed).
  - Judge call (`request_b2b_boolean_judge_output`) is unchanged.

- `runner.py`: no changes.

### Code surface (what does NOT get touched in Task 2)

- No new `request_query_classification()` or `classify_query()` function. Phase A is *variant generation*, not classification. The LLM is not asked to determine the query category, intent, or which heuristics to apply.
- No removal of dropped-paradigm enum tags (`query_syntax_shaping`, `field_and_evidence_targeting`, `tool_and_evidence_mode_targeting`, `discovery_flow`) from `ExpansionParadigm`. Tags stay declared.
- No unification of the duplicate enum hierarchy between `expansion_paradigm_types.py` and `expansion_schemas.py`. The collapsed `SourceLane` enums get the same 8 values in both files, but remain separate enum classes.
- No removal of vestigial fields (`syntax_strategy`, `exclusion_strength`, `target_fields`, `expected_evidence_mode`, `discovery_flow`) from `ExpansionParameters`.

---

## In scope

1. The paradigm classification table above is correctly reflected in the runner's source.
2. Phase A produces a configurable N query variants (default 8) per run via a single LLM call.
3. Phase A's `QueryVariant` schema is implemented, with `variant_id`, `seeds`, `query_body`, and `rationale`.
4. `B2B_QUERY_SPEC` is the single source of per-query truth. Every Phase A call reads from it; every Phase B composition references its `entity_type`.
5. Phase B is pure Python: `SOURCE_LANE_TO_PREFIX` + `NEGATIVES_FOR_SOURCE` + `compose_final_query()`. No LLM call at this layer.
6. The runner's combination set is **generated**: `len(variants) × 8 source_lanes × 2 noise_control options` combinations per run, with default-N = 8 → 128 combinations.
7. Per-run output JSON records, for each candidate, the originating `(variant_id, source_lane, noise_control)` tuple so per-combination YES/NO counts can be rolled up post-hoc.
8. Total LLM calls per run = `1 (variants) + num_combinations × JUDGE_TOP_N`. For default N=8 and `JUDGE_TOP_N=5`: 1 + 128 × 5 = **641 LLM calls per run**.

---

## Out of scope

1. **Classification preanalysis.** No upstream LLM call to determine the query's category, intent, or which paradigms apply. Phase A is *content generation*, not *decision-making*. The runner decides which combinations to test.
2. **LLM-decided combinations.** The runner's combination set is the Cartesian product over (variants × source_lanes × noise_control). The LLM does not choose which combinations to skip or prioritize.
3. **Per-combination LLM rendering calls.** Removed. Phase B is deterministic Python.
4. **Variant filtering by combination.** Every variant is paired with every heuristic combination in the Cartesian. We do not, for example, run `title_broadened` variants only against LinkedIn — they're paired with every source.
5. **Adaptive variant generation.** Phase A produces all N variants in one call. It does not iterate or refine variants based on Phase B's results.
6. **Multi-step pipelines.** No "find companies first, then look inside them for people" workflow. Single-query SERP per combination, as before.
7. **Restructuring of types** beyond what's listed in "Code surface" above. Specifically: NOT in scope is unifying the duplicate enum hierarchy across `expansion_paradigm_types.py` and `expansion_schemas.py`; NOT in scope is removing the vestigial fields on `ExpansionParameters`; NOT in scope is removing dropped-paradigm enum tags from `ExpansionParadigm`.

---

## Accepted trade-offs (explicit risks)

1. **Variant set drift across runs.** Two different runs of the same `B2B_QUERY_SPEC` will produce slightly different variant sets, because Phase A is an LLM call subject to model variance. Within a single run, variants are stable (every combination references the same N variants). Across runs, comparing absolute YES counts requires acknowledging the LLM call as a confound.
2. **Defaults are B2B-shaped.** `B2BQuerySpec`, `SOURCE_LANE_TO_PREFIX`, `NEGATIVES_FOR_SOURCE`, and the LLM paradigm seeds (`title_broadening`, `industry_broadening`, …) are scoped to B2B contact discovery. The runner is not safe to point at non-B2B queries without rewriting these surfaces.
3. **`B2B_QUERY_SPEC` is still hardcoded.** The K query-scoped values are typed by a human in `config.py`. Pointing the runner at a new natural-language query requires editing `B2B_QUERY_SPEC` by hand. Removing this requires real preanalysis (LLM extracts structure from `natural_query`), which is out of scope.
4. **Some Phase B decorators are notional rather than experimentally meaningful.** Including `cognism`, `uplead`, `signalhire` in source lanes will produce results that are mostly paywalled marketing pages. Doing this in the matrix lets us empirically *measure* the gap between paywalled and free sources, but it costs SERP calls for a likely-low signal. Acceptable for now; can be pruned after the first run.
5. **Variant count is a knob, not an optimum.** N = 8 is a default chosen for sane cost (1 + 128 × `JUDGE_TOP_N` calls per run). It's not an experimentally optimal number — too few variants under-samples the seed space; too many bloats the run.

---

## Success criteria

Task 2 is complete when:

1. The paradigm classification table is documented in `experiment.py`'s source (or a referenced comment) such that someone reading the code can verify each row.
2. `request_query_variants()` exists in `llm_request_logic.py` and is the **only** LLM call in the expansion path. `request_expansion_for_combination()` is removed. `COMBINATION_SYSTEM_PROMPT` is removed.
3. `QueryVariant` Pydantic model exists in `expansion_paradigm_types.py` (or `expansion_schemas.py`), with fields `variant_id`, `seeds`, `query_body`, `rationale`.
4. `B2B_QUERY_SPEC` is a single instance in `config.py`. `QUERY` is a derived alias.
5. `B2BQuerySpec` is declared in `expansion_paradigm_types.py` with `entity_type` and `natural_query` required and the other 6 fields `Optional`.
6. `ExpansionParameters` no longer declares the 8 lifted fields (`entity_type`, `industry`, `geography`, `company_type`, `company_size_or_stage`, `role_title_family`, `seniority_band`, `department_or_function`). These fields are absent — not optional-and-unused, absent.
7. `ExpansionParameterSourceLane` and `ExpansionOutputSourceLane` each have exactly 8 values: `linkedin`, `crunchbase`, `theorg`, `cognism`, `uplead`, `kompass`, `signalhire`, `None`.
8. `experiment.py` defines `SOURCE_LANE_TO_PREFIX`, `NEGATIVES_FOR_SOURCE`, `compose_final_query()`, and `target_fields_for(entity_type)` as deterministic Python helpers. No LLM call inside any of them.
9. A run of `python runner.py` produces an `outputs/b2b_<UTC>.json` file with:
   - `b2b_query_spec` at top level (serialized `B2B_QUERY_SPEC`).
   - `variants[]` — the N variants Phase A produced, each with `variant_id`, `seeds`, `query_body`, `rationale`.
   - `records[]` — one entry per `(variant_id, source_lane, noise_control)` × top-N candidate. Each record's `expansion.query` matches `compose_final_query(variant, lane, noise_control)` exactly.
   - Every record's `boolean_summary` populated (when `SKIP_JUDGE = False`).
10. Total LLM calls per run equals exactly `1 + N × |source_lanes| × |noise_control_options| × JUDGE_TOP_N`. For default N=8, that's `1 + 128 × 5 = 641` (or `1 + 128 × 0 = 1` if `SKIP_JUDGE`).
11. Every final query in a record's `expansion.query` starts with `SOURCE_LANE_TO_PREFIX[lane]` (or no prefix for `None`) and ends with the configured negatives when `noise_control=apply`.

---

## Dependencies on prior work

| Prior artifact | Role for Task 2 |
|---|---|
| `devdocs/scoped/1/desc.md` | Original Task 1 description. Task 2 narrows the scope by committing to the two-phase no-classification design. |
| `devdocs/scoped/1/one_by_one_work_logic.md` | Step-by-step description of the runner under the old per-combination LLM call model. Task 2 supersedes this (the per-combination LLM call goes away). |
| `devdocs/scoped/1/how_should_be.md` | Aspirational design with factor flags and atoms. Task 2's two-phase architecture is the implementation of the atoms-once design discussed there. |
| `devdocs/sensemaking/paradigms-preanalysis-requirements.md` | Establishes the per-paradigm mode classification that drove Task 2's paradigm-classification table. |
| `devdocs/scoped/2/scope_drops_and_logic_fixes.md` | Decision archaeology for Task 2: rationale for the 4 dropped paradigms and the 1 lifted paradigm. `desc.md` describes the final state; that file describes how we got there. |

---

## What Task 2 deliberately is NOT

To prevent scope creep, the following are explicitly NOT Task 2's job:

- Task 2 is not a refactor of the duplicate enum hierarchy.
- Task 2 is not a redesign of the judge or the SERP retrieval layer.
- Task 2 is not a comparison study against a preanalysis-enabled runner.
- Task 2 is not "add classification preanalysis behind a flag" — variant generation (Phase A) is not classification.
- Task 2 is not "factor flags inside combinations" — the per-combination toggle model is replaced by variant selection (Phase A) + heuristic decoration (Phase B).
- Task 2 is not "drop the LLM entirely" — the LLM is still doing semantic broadening; it's just doing it once per run instead of per combination.

Task 2 is: **commit to the two-phase architecture, define what Phase A and Phase B do, verify the code matches, run it, save the baseline.**
