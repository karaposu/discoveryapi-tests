# B2B Contact Data Expansion Paradigms

## Purpose

This document defines expansion paradigms for `b2b_contact_data`.

The goal is to generate structured search expansions with Gemini Flash 2.5 instead of testing random prompt rewrites.

This is **not** a test result and does **not** choose a winning prompt.

Use this as the design map for later prompt variants.

## Core Definitions

### Paradigm

A paradigm is a reusable way to transform or target the original query.

Example:

```text
source-lane targeting
```

### Parameter

A parameter is a controlled setting inside a paradigm.

Example:

```text
source_lane = linkedin_person
```

### Recipe

A recipe is a named combination of paradigms and parameters.

Example:

```text
Source-Aware Person-First = entity targeting + source-lane targeting + title normalization + exclusion-aware expansion
```

### Structured Expansion

A structured expansion is the actual Gemini output object.

It contains the search query plus metadata explaining why that query exists and how it should be evaluated.

## Paradigm Groups

### 1. Intent And Terminology

Transforms the wording of the original query while preserving its intent.

Useful when the same B2B role or company type appears under different terms.

Parameters:

- `role_title_family`
- `seniority_band`
- `department_or_function`
- `industry_terms`
- `synonym_style`

Examples:

- `Head of Sales` -> `VP Sales`
- `sales leader` -> `Chief Revenue Officer`
- `cybersecurity SaaS` -> `security software`

Risks:

- Broad synonyms can drift away from the original query.
- Seniority can be changed accidentally.

### 2. Entity Targeting

Chooses what kind of B2B result the expansion is trying to find.

Parameters:

- `entity_type = person_profile`
- `entity_type = company_profile`
- `entity_type = mixed_person_company`

Risks:

- Person and company results need different fields.
- Mixing entity types can make evaluation unclear.

### 3. Discovery Flow

Chooses the discovery path.

Parameters:

- `discovery_flow = person_first`
- `discovery_flow = company_first`
- `discovery_flow = company_then_person`
- `discovery_flow = mixed`

Examples:

- Person-first: find heads of sales directly.
- Company-first: find cybersecurity SaaS companies first.
- Company-then-person: find companies, then discover sales leaders inside them.

Risks:

- Company-first can find good companies but no contacts.
- Person-first can find profiles outside the requested company type.

### 4. Source-Lane Targeting

Targets a specific source or source type.

Parameters:

- `source_lane = linkedin_person`
- `source_lane = linkedin_company`
- `source_lane = crunchbase_person`
- `source_lane = crunchbase_organization`
- `source_lane = company_team_page`
- `source_lane = general_web`

Examples:

```text
site:linkedin.com/in "VP Sales" "cybersecurity SaaS"
site:linkedin.com/company "cybersecurity SaaS"
site:crunchbase.com/organization cybersecurity SaaS
```

Risks:

- Source-specific search can miss good results from other sources.
- Some sources may be blocked, incomplete, or poorly indexed.

### 5. Constraint Handling

Controls which original query constraints are preserved and which are broadened.

Parameters:

- `constraints_preserved`
- `constraints_broadened`
- `broadening_axis`
- `constraint_strictness = strict | moderate | broad`

Common constraints:

- role/title,
- seniority,
- industry,
- geography,
- company type,
- company size or stage.

Rule:

```text
Broaden one axis at a time when possible.
```

Risks:

- Hidden broadening makes results hard to interpret.
- Strict constraints can miss useful results.

### 6. Field And Evidence Targeting

Biases expansions toward results likely to expose fields from the Category Output Contract.

Parameters:

- `target_fields`
- `expected_evidence_mode`
- `field_intent = identity | role_fit | company_fit | firmographics | provenance`

Person target fields:

- `person_name`
- `current_title`
- `current_company`
- `profile_or_source_url`
- `work_history`
- `skills`

Company target fields:

- `company_name`
- `company_domain_or_profile_url`
- `industry_or_description`
- `headcount_or_company_size`
- `funding`
- `headquarters_or_location`

Risks:

- Adding too many field terms can make queries unnatural.
- Snippet-only results may not expose the fields even when the page is relevant.

### 7. Noise Control

Adds explicit intent to avoid known bad result types.

Parameters:

- `exclusions`
- `exclusion_strength = light | moderate | strict`

Common exclusions:

- job postings,
- career advice,
- resume templates,
- HR software pages,
- recruiting software pages,
- staffing agency marketing,
- generic HR blogs,
- generic lead lists without evidence.

Risks:

- Negative syntax may not work consistently across retrieval methods.
- Over-exclusion can remove useful results.

### 8. Query Syntax Shaping

Controls how the query is expressed for retrieval.

Parameters:

- `syntax_strategy = natural_language`
- `syntax_strategy = quoted_phrase`
- `syntax_strategy = site_operator`
- `syntax_strategy = boolean_or`
- `syntax_strategy = negative_terms`
- `syntax_strategy = exact_title`

Examples:

```text
"VP Sales" OR "Head of Sales"
site:linkedin.com/in
-jobs
```

Risks:

- Syntax support may vary by search provider.
- Overly complex syntax can reduce recall.

### 9. Tool And Evidence-Mode Targeting

Shapes the expansion for the kind of downstream evidence expected.

Parameters:

- `expected_evidence_mode = snippet_only`
- `expected_evidence_mode = content`
- `expected_evidence_mode = structured_enrichment`
- `enrichment_hint`

Examples:

- SERP query for URL discovery.
- Dataset/entity lookup for company names.
- WSAPI route hint for LinkedIn or Crunchbase enrichment.

Risks:

- Tool-aware expansion can overfit to a tool that is not available.
- Evidence assumptions must be marked clearly.

## Main Parameter Dimensions

| Parameter | Example Values |
|---|---|
| `entity_type` | `person_profile`, `company_profile`, `mixed_person_company` |
| `discovery_flow` | `person_first`, `company_first`, `company_then_person`, `mixed` |
| `source_lane` | `linkedin_person`, `linkedin_company`, `crunchbase_person`, `crunchbase_organization`, `company_team_page`, `general_web` |
| `role_title_family` | `sales_leadership`, `engineering_leadership`, `marketing_leadership`, `security_leadership` |
| `seniority_band` | `executive`, `vp`, `director`, `manager`, `individual_contributor` |
| `department_or_function` | `sales`, `security`, `engineering`, `marketing`, `operations` |
| `industry` | `cybersecurity`, `SaaS`, `fintech`, `healthtech`, `AI` |
| `geography` | `United States`, `Europe`, `UK`, `remote`, `global` |
| `company_type` | `SaaS`, `startup`, `enterprise`, `agency`, `vendor` |
| `company_size_or_stage` | `startup`, `growth`, `enterprise`, `funded`, `public` |
| `constraints_preserved` | role, industry, geography, seniority, company type |
| `constraints_broadened` | title, industry, geography, source, company type |
| `broadening_axis` | `title`, `industry`, `geography`, `source`, `company_type`, `none` |
| `target_fields` | fields from `task/b2b_contact_data_category_output_contract.md` |
| `exclusions` | jobs, HR blogs, career advice, recruiting software, generic directories |
| `expected_evidence_mode` | `snippet_only`, `content`, `structured_enrichment` |
| `syntax_strategy` | `natural_language`, `quoted_phrase`, `site_operator`, `boolean_or`, `negative_terms`, `exact_title` |

## Structured Expansion Schema

### Required Fields

```yaml
expansion_id:
paradigms:
entity_type:
discovery_flow:
source_lane:
query:
constraints:
  preserved:
  broadened:
target_fields:
exclusions:
expected_evidence_mode:
risk_notes:
```

### Optional Fields

```yaml
broadening_axis:
syntax_strategy:
enrichment_hint:
diagnostic_purpose:
```

## Example Structured Expansion

```yaml
expansion_id: source_person_001
paradigms:
  - source_lane_targeting
  - person_first
  - title_normalization
  - exclusion_aware
entity_type: person_profile
discovery_flow: person_first
source_lane: linkedin_person
query: 'site:linkedin.com/in ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" "United States"'
constraints:
  preserved:
    - role: sales leadership
    - industry: cybersecurity SaaS
    - geography: United States
  broadened:
    - title: Head of Sales -> VP Sales
target_fields:
  - person_name
  - current_title
  - current_company
  - profile_or_source_url
exclusions:
  - job_postings
  - career_advice
  - hr_software_pages
expected_evidence_mode: snippet_only
risk_notes:
  - May miss profiles that do not include exact industry wording.
```

## Candidate Recipes To Test Later

These are candidate combinations, not winners.

### 1. Broad Semantic Recall

Purpose:

Find more potentially relevant results by expanding terminology.

Combines:

- intent and terminology,
- controlled broadening,
- light noise control.

Useful when:

- role/title language varies,
- industry wording varies,
- recall is too low.

Main risk:

- More noisy results.

### 2. Strict Constraint-Preserving

Purpose:

Keep the original query as intact as possible.

Combines:

- constraint handling,
- exact title or phrase syntax,
- strict exclusions.

Useful when:

- broad expansions drift too much,
- the query has strong filters.

Main risk:

- Misses useful profiles with different wording.

### 3. Source-Aware Person-First

Purpose:

Find individual professional profiles directly.

Combines:

- entity targeting: `person_profile`,
- discovery flow: `person_first`,
- source-lane targeting,
- title normalization,
- exclusion-aware expansion.

Useful when:

- the target role is clear,
- LinkedIn or Crunchbase person results are expected.

Main risk:

- Returns people outside the requested company type or geography.

### 4. Source-Aware Company-First

Purpose:

Find target companies before looking for people.

Combines:

- entity targeting: `company_profile`,
- discovery flow: `company_first`,
- source-lane targeting,
- firmographic field targeting.

Useful when:

- direct person search is sparse,
- company fit matters strongly.

Main risk:

- Finds companies but not contacts.

### 5. Field-Intent Enriched-Data

Purpose:

Generate expansions likely to return sources with useful fields.

Combines:

- field and evidence targeting,
- source-lane targeting,
- tool/evidence-mode targeting.

Useful when:

- later enrichment will run,
- field coverage matters.

Main risk:

- Query may become unnatural or too constrained.

### 6. Exclusion-Heavy Precision

Purpose:

Reduce predictable B2B noise.

Combines:

- noise control,
- query syntax shaping,
- constraint preservation.

Useful when:

- results contain job postings, HR blogs, career advice, or software pages.

Main risk:

- Negative terms may suppress useful results.

### 7. Company-First Then Person-Followup

Purpose:

Use company discovery as a first step, then search for target roles inside those companies.

Combines:

- company-first flow,
- firmographic field targeting,
- person-followup query generation.

Useful when:

- target companies are easier to identify than target people.

Main risk:

- Requires a second-stage workflow, not just a single query list.

### 8. Diagnostic Contrast

Purpose:

Generate intentionally different expansions to expose where noise or recall problems come from.

Combines:

- broad recall,
- strict precision,
- source contrast,
- exclusion contrast.

Useful when:

- we do not know whether failures come from source choice, title wording, constraints, or noise.

Main risk:

- Not necessarily the best production strategy; it is mainly diagnostic.

## Anti-Patterns

Do not generate random prompt rewrites without metadata.

Do not treat one paradigm as a full prompt variant.

Do not generate the full Cartesian product of all parameters.

Do not broaden multiple hard constraints at once unless the recipe explicitly says so.

Do not rely only on query syntax to express exclusions.

Do not require private email or phone discovery unless the task scope changes.

Do not make every diagnostic field required in the structured expansion output.

## How This Connects To Task 1

Task 1 should use this document before writing Gemini Flash 2.5 prompt variants.

The flow should be:

```text
original query
-> choose recipe
-> set parameter values
-> Gemini generates structured expansions
-> retrieval uses expansion.query
-> evaluation uses expansion metadata + returned results
```

This lets us compare expansion prompts while still understanding what each prompt actually changed.
