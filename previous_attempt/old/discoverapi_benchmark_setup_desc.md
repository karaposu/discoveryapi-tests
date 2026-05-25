# Discover API Diagnostic Benchmark Setup - Description

## Purpose

This document defines the **Diagnostic Benchmark Setup** for the Discover API architecture benchmark.

The Diagnostic Benchmark Setup is not the benchmark result. It is the set of setup decisions, rules, schemas, and checklists needed before running the Diagnostic Benchmark Setup Validation Run.

The setup should answer:

- What do we need to ask Shahar/backend?
- What can we learn ourselves from the SDK/repo?
- What must be checked in Tavily and Exa docs before fair comparison?
- What counts as a good result for the setup validation category?
- How will nDCG@5, HFTE, and throughput be measured?
- What run artifacts must be stored?
- What internal trace data, or final-output-only evidence, is needed to explain failures?
- What gates must pass before running 50-query category reports?

## Important Separation

There are two different things:

1. **Preparation understanding** - how much we know about current Discover internals.
2. **Diagnostic Benchmark Setup** - the actual benchmark rules and artifacts we create.

These should not be mixed.

For example, we can create the Diagnostic Benchmark Setup even if we only have final Discover outputs. But if we do not have internal traces or middle products, the benchmark can only infer failure causes from final results. Those architecture-cause claims must be marked as inferred, not confirmed.

## Preparation Understanding Levels

Preparation understanding describes how much evidence we have about current Discover internals.

It is not the setup itself. It is the evidence level that affects how strong the setup can be.

| Understanding | What We Know | What It Enables | What Cannot Be Done Yet | What Is Still Weak |
|---|---|---|---|---|
| Public-output only | We can call Discover and inspect final returned results | Final-output benchmark planning | We cannot prove which internal stage caused a failure. | Internal failure attribution is weak. |
| High-level backend explanation | Shahar confirms the pipeline at a conceptual level | Better question sheet and architecture assumptions | We cannot prove why a specific query failed. | Per-query causes are still inferred from final outputs. |
| Static middle-product examples | We have 1-2 sample runs with expanded queries, lanes, candidates, reranking, enrichment, and final output | Trace schema and failure taxonomy grounded in real examples | We cannot confirm stage behavior for our setup validation query set. | Samples may not represent our Diagnostic Benchmark Setup Validation Run. |
| Debug traces for the Diagnostic Benchmark Setup Validation Run | The setup validation run includes stage evidence | High-confidence failure attribution for the setup validation run | We still cannot freely test architecture variants unless variant controls exist. | Requires trace access and data handling. |
| Internal runnable/staging access | We can run or inspect internal variants directly | Strongest architecture experiments | We still cannot claim production impact until tested against representative queries and production-like constraints. | This becomes harness/integration work, not only readiness planning. |

### Target Preparation Understanding

Minimum acceptable:

**High-level backend explanation.**

Preferred:

**Static middle-product examples.**

Best for setup validation:

**Debug traces for the Diagnostic Benchmark Setup Validation Run.**

Do not assume internal runnable or staging access unless Shahar explicitly says it is already stable and easy to use.

## Diagnostic Benchmark Setup Scope

The Diagnostic Benchmark Setup is the artifact set we create to make the Diagnostic Benchmark Setup Validation Run possible.

The target setup should be:

**A small setup that can be validated before scaling to category reports.**

This means the setup should define everything needed to run the Diagnostic Benchmark Setup Validation Run:

- what systems/configs to run,
- what category and query shape to use,
- what a useful output must contain,
- how results will be judged,
- how nDCG@5, HFTE, and throughput will be computed,
- what data must be stored,
- how failures will be attributed,
- what gates decide whether we can move to 50-query category reports.

The setup should support two evidence modes:

1. **Trace-based failure attribution** - if Shahar/backend can provide middle products or debug traces.
2. **Final-output-only failure inference** - if we only have final returned results.

Trace-based failure attribution is preferred because it connects benchmark scores to actual pipeline stages. Final-output-only failure inference is acceptable as a fallback, but architecture conclusions from it must be marked lower confidence.

## How Preparation Understanding Changes The Setup

The setup scope stays mostly the same, but the confidence changes.

| Preparation Understanding | Evidence Mode | What Changes In The Setup |
|---|---|---|
| Public-output only | Final-output-only failure inference | Failure attribution uses final URLs, content, errors, latency, enrichment hints, and judge labels. |
| High-level backend explanation | Final-output-only failure inference with better assumptions | Architecture assumptions are clearer, but per-query causes are still inferred. |
| Static middle-product examples | Trace-schema-informed mode | Trace schema and failure labels are grounded in real examples. |
| Debug traces for the Diagnostic Benchmark Setup Validation Run | Trace-based failure attribution | Metrics from the setup validation run can be joined to actual stage evidence. |
| Internal runnable/staging access | Upgraded mode | Scope expands beyond setup into integration/harness work. |

Default target:

- Create the Diagnostic Benchmark Setup now.
- Use static middle-product examples if Shahar can provide them.
- Use high-level backend explanation or public-output-only evidence with final-output-only failure inference if Shahar cannot provide middle products yet.
- Upgrade to debug traces for the Diagnostic Benchmark Setup Validation Run if traces are easy to access.
- Treat internal runnable/staging access as out of baseline scope.

## Done Criteria For The Diagnostic Benchmark Setup

The Diagnostic Benchmark Setup is done when all of the following are true.

### 1. Scope And Assumptions Are Fixed

- [ ] The preparation understanding is stated: public-output only, high-level backend explanation, static middle-product examples, debug traces for the Diagnostic Benchmark Setup Validation Run, or internal runnable/staging access.
- [ ] The evidence mode is stated: trace-based failure attribution or final-output-only failure inference.
- [ ] Active work estimate and elapsed-time blockers are separated.
- [ ] Out-of-scope items are listed, especially full automation and internal harness work.
- [ ] Open blockers are marked by owner: Shahar/backend, local repo, external docs, or setup validation evidence.

### 2. Shahar/Backend Question Sheet Exists

- [ ] It asks how category is selected or inferred.
- [ ] It asks for current categories and subcategories/search lanes.
- [ ] It asks for Gemini expansion model, prompt, and sample expanded queries.
- [ ] It asks for raw SERP candidates per lane.
- [ ] It asks for dedupe logic and candidate counts.
- [ ] It asks for Voyage model/version, reranker input, reranker instruction, scores, and output order.
- [ ] It asks for top-K before enrichment.
- [ ] It asks for WSAPI, dataset, and Web Unlocker routing rules.
- [ ] It asks for enrichment failures, fallback rules, stage errors, and stage latencies.
- [ ] It asks for static middle-product examples at minimum.
- [ ] It asks whether debug traces for the Diagnostic Benchmark Setup Validation Run are available.
- [ ] It asks whether internal runnable/staging access exists, but treats that as optional.

### 3. Local Source And Enrichment Matrix Exists

- [ ] It lists candidate sources/search lanes per category.
- [ ] It lists possible enrichment methods per source: WSAPI/platform scraper, dataset, Web Unlocker, or other.
- [ ] It lists expected useful fields per source.
- [ ] It marks whether evidence comes from local SDK/repo inventory or confirmed production routing.
- [ ] It includes source risks such as blocking, compliance, freshness, or unsupported structured extraction.

### 4. Competitor Fair-Run Checklist Exists

- [ ] Tavily settings to research are listed.
- [ ] Exa settings to research are listed.
- [ ] Result count, content depth, filters, freshness, domains, locale, timeout, and retries are included.
- [ ] Output shape differences are listed as normalization risks.
- [ ] Any unknown costs or rate limits are marked as blockers before full comparison.

### 5. Setup Validation Category And Query Shape Are Defined

- [ ] The setup validation category is selected or the decision rule is stated.
- [ ] The reason for the setup validation category is recorded: diagnostic value, access, source diversity, enrichment difficulty, and priority.
- [ ] The setup validation query count is stated.
- [ ] Query diversity requirements are stated.
- [ ] The Diagnostic Benchmark Setup Validation Run's job is stated: validate the setup, not prove final product performance.

### 6. Category Output Contract Exists For The Setup Validation Category

- [ ] Required useful fields are defined.
- [ ] Optional useful fields are defined.
- [ ] Source preferences and source exclusions are defined.
- [ ] Freshness requirements are defined.
- [ ] Category-specific noise is defined.
- [ ] The contract can be used by both the judge and the HFTE calculation.
- [ ] The contract defines what useful output should contain for this category, independent of which system produced it.

### 7. nDCG@5 Relevance Rubric Exists

- [ ] Relevance grades are defined, for example 0-3 or 0-4.
- [ ] Each grade has plain-language criteria.
- [ ] Examples of good, partial, weak, and irrelevant results are included or marked as needed.
- [ ] The rubric explicitly says system scores such as Voyage relevance score are not ground-truth labels.
- [ ] Labels are based on pooled results across systems, not one system's output.

### 8. HFTE Definition Exists

- [ ] "Relevant signal" is defined for the setup validation category.
- [ ] Total token counting rule is defined.
- [ ] Boilerplate, navigation, ads, unrelated text, and low-value content are treated as token cost.
- [ ] The setup states that shorter output is not automatically better if required useful fields are missing.

### 9. Judging And Human Audit Plan Exists

- [ ] Result pooling process is defined.
- [ ] URL and entity deduplication process is defined.
- [ ] LLM-assisted labeling workflow is defined.
- [ ] Human audit sample rule is defined.
- [ ] Top-5 results and borderline labels get special audit attention.
- [ ] Label correction and label freeze process is defined.
- [ ] Agreement threshold is defined or marked as a Shahar/product decision.

### 10. Run Manifest And Output Schemas Exist

- [ ] Run manifest includes query, category, system, config, timestamp, locale, timeout, retries, result count, include-content setting, and variant ID.
- [ ] Raw output schema is defined.
- [ ] Normalized output schema is defined.
- [ ] Required join keys are defined.
- [ ] Storage/reproducibility expectations are defined.

### 11. Trace Schema Or Final-Output-Only Failure Inference Exists

- [ ] Trace schema includes expected fields for expanded queries, search lanes, raw candidates, dedupe, reranking, top-K, enrichment route, fallback, errors, and latency.
- [ ] If backend traces are unavailable, final-output-only inference fields are defined.
- [ ] Final-output-only inference fields include returned URL, source/domain, content availability, structured-field presence, latency, errors, enrichment indicators, and judge/failure labels.
- [ ] The setup states that final-output-only architecture conclusions are inferred, not confirmed.

### 12. Failure Attribution Ledger Exists

- [ ] Failure labels are defined at query/system/config level.
- [ ] Result-level detail is reserved for top-5 failures, enrichment failures, and audit samples.
- [ ] Failure stages include expansion, category routing, source/lane selection, raw recall, dedupe, reranking, enrichment routing, extraction, fallback, schema, freshness, throughput, and judging.
- [ ] Each failure label has a short definition.

### 13. Setup Validation Gates Exist

- [ ] Setup-validation-start gates are defined.
- [ ] Setup-validation-pass gates are defined.
- [ ] Full 50-query report gates are defined.
- [ ] The setup states that final category reports should not start until the Diagnostic Benchmark Setup Validation Run proves judging, metrics, artifacts, and failure attribution.

### 14. Reusable Report Template Exists

- [ ] The report template includes system comparison.
- [ ] It includes nDCG@5, HFTE, and throughput sections.
- [ ] It includes failure-mode breakdown.
- [ ] It includes Category Output Contract compliance.
- [ ] It includes architecture recommendation.
- [ ] It includes evidence appendix requirements: queries, manifests, labels, examples, and configs.

## Explicitly Out Of Scope

The Diagnostic Benchmark Setup should not include:

- full benchmark automation,
- a production benchmark platform,
- internal staging/harness integration unless explicitly approved,
- final 50-query category reports,
- bundled architecture variants,
- final architecture recommendations,
- full query sets for all categories,
- full human labeling of all results.

## Completion Statement

The Diagnostic Benchmark Setup is complete when the Diagnostic Benchmark Setup Validation Run can be started with clear rules, known blockers, reproducible artifacts, defined judging, defined metrics, a Category Output Contract, and either trace-based failure attribution or final-output-only failure inference.

If an artifact only helps us talk about the benchmark but does not define how to run and judge the Diagnostic Benchmark Setup Validation Run, it is preparation material, not part of the Diagnostic Benchmark Setup itself.
