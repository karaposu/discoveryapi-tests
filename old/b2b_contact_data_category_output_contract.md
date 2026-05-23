# B2B Contact Data Category Output Contract

## Purpose

This contract defines what counts as a useful `b2b_contact_data` result for benchmark judging.

Use it to judge Task 1 expansion-prompt results, compute relevance labels for nDCG@5, measure Category Output Contract coverage, and support later HFTE calculation when enriched/content payloads exist.

This is a **benchmark evaluation contract**, not a production API schema.

## Scope

The category is:

```text
b2b_contact_data
```

The target use cases are:

- AI sales development representatives,
- lead generation platforms,
- talent mapping,
- CRM enrichment,
- company and firmographic discovery.

Useful results should help discover or enrich:

- professional profiles,
- current role and company,
- work history or professional context,
- company firmographics such as industry, headcount, location, and funding.

## Evidence Modes

Field credit depends on what evidence the run returns.

| Evidence Mode | Available Evidence | What Can Be Judged |
|---|---|---|
| `snippet_only` | URL, title, snippet | Relevance, source fit, visible field hints only |
| `content` | Page text, markdown, extracted body | Relevance and visible field coverage |
| `structured_enrichment` | WSAPI, dataset, scraper, or structured fields | Relevance, full field coverage, and HFTE support |

Do not credit fields that are not visible in the returned evidence.

## Output Item Types

| Type | Meaning |
|---|---|
| `person_profile` | A public professional profile or person page. |
| `company_profile` | A company page or company firmographic record. |
| `mixed_person_company` | A result that contains useful person and company information. |
| `noise` | A result that should receive low or zero relevance. |

## Person Profile Fields

### Required Core Fields

A useful `person_profile` should contain:

| Field | Description |
|---|---|
| `person_name` | The identified professional. |
| `current_title` | Current role, title, or seniority. |
| `current_company` | Current employer or organization. |
| `profile_or_source_url` | Professional profile URL or source URL. |
| `evidence_source` | Source that supports the claim. |

### Useful Extra Fields

These improve field coverage but are not required for a minimally useful result:

- `location`
- `seniority`
- `department_or_function`
- `work_history`
- `tenure`
- `education`
- `skills`
- `professional_summary`

## Company Profile Fields

### Required Core Fields

A useful `company_profile` should contain:

| Field | Description |
|---|---|
| `company_name` | The identified company. |
| `company_domain_or_profile_url` | Company domain, LinkedIn company URL, Crunchbase URL, or equivalent. |
| `industry_or_description` | What the company does or which industry it belongs to. |
| `evidence_source` | Source that supports the claim. |

### Useful Extra Fields

These improve field coverage but are not required for a minimally useful result:

- `headquarters_or_location`
- `headcount_or_company_size`
- `funding`
- `investors`
- `employee_count`
- `founded_year`
- `growth_signal`
- `relevant_employee_or_profile_links`

## Contact Detail Policy

Do not require:

- personal email,
- phone number,
- personal address,
- private contact details.

These fields can be recorded only if they are explicitly visible, public, and allowed by data handling rules.

They should not be part of the required score unless Shahar explicitly expands the task to outbound contact-detail enrichment.

## Exclusions And Noise

Score these as `0` or `1` depending on whether they contain any useful evidence:

- job postings,
- career advice pages,
- resume templates,
- HR software marketing pages,
- recruiting software marketing pages,
- staffing agency marketing pages,
- generic HR blogs,
- generic lead-list pages without field-level evidence,
- pages in the wrong industry,
- pages in the wrong geography when geography is requested,
- pages for the wrong entity type,
- pages that mention the query terms but do not expose useful B2B fields.

## Relevance Grade For nDCG@5

Use this grade for ranking metrics.

| Grade | Meaning | Criteria |
|---:|---|---|
| `3` | Excellent B2B result | Correct entity type, matches query constraints, credible source, strong useful fields. |
| `2` | Useful B2B result | Correct entity type and intent, enough evidence to be useful, but some important fields are missing. |
| `1` | Weak or partial result | Related to the query, but missing important fields, weak evidence, or only indirectly useful. |
| `0` | Irrelevant or noise | Wrong entity type, job post, blog, marketing page, wrong industry/geography, or no usable evidence. |

The grade should reflect query fit and evidence quality, not only field count.

## Field Coverage Score

Use field coverage to measure how much useful B2B data the result contains.

### Person Field Coverage

Core person fields: 5 possible points.

- `person_name`
- `current_title`
- `current_company`
- `profile_or_source_url`
- `evidence_source`

Extra person fields: up to 8 possible points.

- `location`
- `seniority`
- `department_or_function`
- `work_history`
- `tenure`
- `education`
- `skills`
- `professional_summary`

### Company Field Coverage

Core company fields: 4 possible points.

- `company_name`
- `company_domain_or_profile_url`
- `industry_or_description`
- `evidence_source`

Extra company fields: up to 8 possible points.

- `headquarters_or_location`
- `headcount_or_company_size`
- `funding`
- `investors`
- `employee_count`
- `founded_year`
- `growth_signal`
- `relevant_employee_or_profile_links`

### Formula

```text
field_coverage = credited_points / possible_points_for_item_type
```

For `mixed_person_company`, score person and company coverage separately, then report both.

## Metric Usage

| Metric | When Valid | Notes |
|---|---|---|
| nDCG@5 | Ranked candidates exist and each candidate has a relevance grade. | Uses the `0-3` relevance grade. |
| Category Output Contract coverage | Returned evidence exposes fields. | Uses the field coverage score. |
| HFTE | Enriched/content payloads exist and token count can be measured. | Do not compute from expansion strings alone. |
| Noise rate | Any retrieval output exists. | Count results marked `noise` or grade `0`. |

## LLM Judge Output

For each result, the judge should output:

```text
item_type:
relevance_grade:
credited_fields:
missing_important_fields:
failure_tags:
evidence_note:
confidence:
```

The judge must not credit fields that are not visible in the provided evidence.

## Human Audit

Audit at least:

- all prompt winners,
- all close prompt comparisons,
- a sample of rejected/noisy results,
- a sample per source lane,
- any result where the judge used low confidence.

## Open Questions

- Does Shahar want email or phone to become required fields later?
- Will the first Task 1 run use `snippet_only`, `content`, or `structured_enrichment` evidence?
- Which judge model and audit rate will be used?
