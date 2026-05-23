# B2B Contact Data Typed Expansion Schema

## Purpose

This document defines the typed output shape for Gemini Flash 2.5 query expansions in Task 1.

Gemini should not return plain strings only.

The schema should make first experiments reproducible and diagnosable without modeling the whole benchmark pipeline.

## Recommendation

Use three top-level lifecycle schemas:

```text
ExpansionExperimentConfig
ExpansionInputData
ExpansionOutputResult
```

Also use one nested per-expansion item:

```text
ExpansionOutputItem
```

Gemini should return only:

```text
ExpansionOutputResult
```

The benchmark runner owns `ExpansionExperimentConfig`.

The prompt receives `ExpansionInputData`.

`ExpansionOutputResult` contains:

```text
expansions: list[ExpansionOutputItem]
```

## Why Not A Single Flat Schema?

The compact schema is a good start:

```text
entity_type
source_lane
query
expected_fields
exclusions
```

But it is too thin as the full schema.

It does not say:

- which prompt/config produced the expansion,
- which constraints were preserved,
- which constraints were broadened,
- which expansion paradigm was used,
- whether the query expects snippet-only evidence or enriched structured evidence,
- what known risk the expansion has.

Without this metadata, we can still run searches, but we cannot clearly explain why one expansion prompt performs better or worse than another.

## Model Responsibilities

### ExpansionExperimentConfig

Runner-owned fixed settings for a comparison.

Gemini should not generate this.

Use this to keep prompt comparisons fair.

Typical fields:

- category,
- Gemini model,
- prompt version,
- number of expansions,
- allowed entity types,
- allowed source lanes,
- allowed field names,
- allowed evidence modes.

### ExpansionInputData

Input context supplied to Gemini.

This is not retrieved data from LinkedIn, Crunchbase, or the web.

It is the input data for the expansion step.

Typical fields:

- original query,
- parsed or declared constraints,
- category output contract reference,
- allowed source lanes,
- allowed exclusions,
- normalized intent.

Naming note:

`ExpansionInputData` is the preferred name because it avoids the old ambiguity around "source data".

### ExpansionOutputResult

Gemini's output for one prompt run.

Typical fields:

- result id,
- prompt version,
- model,
- original query,
- list of generated expansions.

### ExpansionOutputItem

One generated search expansion.

This is where the compact schema belongs.

Required fields:

```text
expansion_id
entity_type
source_lane
query
target_fields
exclusions
expansion_trace
expected_evidence_mode
risk_notes
```

Use `target_fields` instead of `expected_fields`.

Reason:

The expansion is trying to surface those fields. It does not prove that those fields exist in returned evidence.

If prompt wording needs `expected_fields`, define it as an alias for `target_fields` and document that it means "fields this query is trying to surface."

## Expansion Trace

Each expansion should include a structured explanation of how it was expanded.

Do not rely only on a freeform rationale.

Recommended shape:

```text
expansion_trace:
  recipe_name
  paradigms
  preserved_constraints
  broadened_constraints
  broadening_axis
  rationale
```

This lets us group results by:

- expansion recipe,
- paradigm family,
- source lane,
- broadening axis,
- preserved constraints,
- broadened constraints.

## Recommended Enum Values

### Entity Type

Use values aligned with the Category Output Contract:

```text
person_profile
company_profile
mixed_person_company
```

For first experiments, `person_profile` and `company_profile` may be enough.

### Source Lane

Use source-family targets:

```text
linkedin_person
linkedin_company
crunchbase_person
crunchbase_company
company_team_page
general_web
```

`source_lane` is not the same thing as a retrieval tool.

For example, a SERP search can target the `linkedin_person` source lane.

### Evidence Mode

Use values from the Category Output Contract:

```text
snippet_only
content
structured_enrichment
```

## Pydantic-Style Sketch

This is a schema sketch for discussion.

It is not yet an implementation file.

```python
from enum import Enum
from pydantic import BaseModel, Field


class ExpansionOutputEntityType(str, Enum):
    person_profile = "person_profile"
    company_profile = "company_profile"
    mixed_person_company = "mixed_person_company"


class ExpansionOutputSourceLane(str, Enum):
    linkedin_person = "linkedin_person"
    linkedin_company = "linkedin_company"
    crunchbase_person = "crunchbase_person"
    crunchbase_company = "crunchbase_company"
    company_team_page = "company_team_page"
    general_web = "general_web"


class ExpansionOutputEvidenceMode(str, Enum):
    snippet_only = "snippet_only"
    content = "content"
    structured_enrichment = "structured_enrichment"


class ExpansionOutputBroadeningAxis(str, Enum):
    none = "none"
    title = "title"
    industry = "industry"
    geography = "geography"
    source = "source"
    company_type = "company_type"
    seniority = "seniority"


class ExpansionInputConstraintValue(BaseModel):
    name: str
    value: str
    note: str | None = None


class ExpansionOutputConstraintValue(BaseModel):
    name: str
    value: str
    note: str | None = None


class ExpansionOutputTrace(BaseModel):
    recipe_name: str
    paradigms: list[str]
    preserved_constraints: list[ExpansionOutputConstraintValue] = Field(default_factory=list)
    broadened_constraints: list[ExpansionOutputConstraintValue] = Field(default_factory=list)
    broadening_axis: ExpansionOutputBroadeningAxis = ExpansionOutputBroadeningAxis.none
    rationale: str


class ExpansionOutputItem(BaseModel):
    expansion_id: str
    entity_type: ExpansionOutputEntityType
    source_lane: ExpansionOutputSourceLane
    query: str
    target_fields: list[str]
    exclusions: list[str] = Field(default_factory=list)
    expansion_trace: ExpansionOutputTrace
    expected_evidence_mode: ExpansionOutputEvidenceMode
    risk_notes: list[str] = Field(default_factory=list)


class ExpansionExperimentConfig(BaseModel):
    category: str = "b2b_contact_data"
    model: str
    prompt_version: str
    num_expansions: int
    allowed_entity_types: list[ExpansionOutputEntityType]
    allowed_source_lanes: list[ExpansionOutputSourceLane]
    allowed_fields: list[str]
    allowed_evidence_modes: list[ExpansionOutputEvidenceMode]


class ExpansionInputData(BaseModel):
    original_query: str
    normalized_intent: str | None = None
    declared_constraints: list[ExpansionInputConstraintValue] = Field(default_factory=list)
    category_contract_ref: str
    allowed_exclusions: list[str] = Field(default_factory=list)


class ExpansionOutputResult(BaseModel):
    result_id: str
    category: str = "b2b_contact_data"
    model: str
    prompt_version: str
    original_query: str
    expansions: list[ExpansionOutputItem]
```

## Example Gemini Output

Gemini should return an `ExpansionOutputResult`-shaped object:

```yaml
result_id: b2b_sales_001_prompt_a
category: b2b_contact_data
model: gemini-2.5-flash
prompt_version: source_aware_v1
original_query: heads of sales at US cybersecurity SaaS companies
expansions:
  - expansion_id: exp_001
    entity_type: person_profile
    source_lane: linkedin_person
    query: 'site:linkedin.com/in ("Head of Sales" OR "VP Sales") "cybersecurity SaaS" "United States"'
    target_fields:
      - person_name
      - current_title
      - current_company
      - profile_or_source_url
    exclusions:
      - job_postings
      - career_advice
      - recruiting_software_pages
    expected_evidence_mode: snippet_only
    expansion_trace:
      recipe_name: Source-Aware Person-First
      paradigms:
        - source_lane_targeting
        - person_first
        - title_normalization
        - exclusion_aware
      preserved_constraints:
        - role: sales leadership
        - industry: cybersecurity SaaS
        - geography: United States
      broadened_constraints:
        - title: Head of Sales -> VP Sales
      broadening_axis: title
      rationale: Uses LinkedIn person-profile search and broadens title wording while preserving industry and geography.
    risk_notes:
      - May miss people whose profile does not mention cybersecurity SaaS directly.
```

## What Stays Outside This Schema

Do not include these in `ExpansionOutputResult`:

- returned SERP results,
- retrieved page content,
- WSAPI or dataset records,
- relevance grades,
- credited fields,
- nDCG,
- HFTE,
- human audit decisions.

Those belong to later retrieval and evaluation schemas.

## First-Experiment Decision

This schema is good enough for first experiments if:

- Gemini reliably returns valid JSON,
- each expansion has a query and source lane,
- each expansion has target fields and exclusions,
- each expansion has a structured trace,
- the runner keeps config fixed across prompt variants.

If Gemini struggles with this shape, simplify first by making optional fields optional.

Do not remove `expansion_trace` unless the experiment no longer needs to explain why a prompt wins or fails.
