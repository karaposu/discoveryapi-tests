# Shahar / Backend Question Sheet - Discover API Benchmark

## Purpose

We need these answers to create the Discover API benchmark-readiness package and avoid running misleading category reports.

The main goal is to understand enough of the current Discover API architecture to run a Diagnostic Benchmark Setup Validation Run. That validation run should explain where Discover succeeds or fails: query expansion, source/search lane, raw recall, dedupe, reranking, enrichment, fallback, schema, freshness, or throughput.

## Short Version

Minimum useful ask:

- Can you confirm the current production Discover pipeline at a high level?
- Can you provide 1-2 sample runs with middle products, not only final output?
- Can you tell us which middle products or debug traces can be exposed for the Diagnostic Benchmark Setup Validation Run?

Preferred ask:

- Debug traces for the Diagnostic Benchmark Setup Validation Run, including expanded queries, search lanes, raw candidates, reranker output, enrichment routing, final output, errors, and timings.

Optional upgraded ask:

- Internal runnable/staging access, only if this is already stable and easy to use.

## P0 - Critical Questions

These are required before we can make high-confidence architecture claims.

### 1. Current Pipeline Confirmation

- Is the current Discover API production pipeline still roughly:
  1. Gemini semantic expansion,
  2. category-specific SERP/search-lane fan-out,
  3. Voyage reranking,
  4. WSAPI/dataset/Web Unlocker enrichment?
- If this is not accurate, what is the current production pipeline?
- Are there different pipelines for different categories?
- Is the public SDK `/discover` endpoint using the same pipeline described in the task source, or is that an internal/research architecture?

### 2. Category Selection

- How does Discover know the category for a query?
- Is category passed explicitly, inferred from query/intent, selected by an internal workflow, or not part of the public Discover path?
- What are the current production categories?
- Are the seven benchmark categories already supported internally?
  - `b2b_contact_data`
  - `price_intelligence`
  - `social_media_video`
  - `job_market`
  - `news_media`
  - `real_estate`
  - `financial_data`
- Are there existing subcategories/search lanes for these categories?

### 3. Query Expansion

- Which model performs semantic expansion?
- Is it Gemini? If yes, which model/version?
- What prompt or instruction is used for expansion?
- How many expanded queries are generated per input query?
- Are expanded queries category-specific?
- Can we see example expanded queries for 1-2 real inputs?
- Can expanded queries be logged or returned for the Diagnostic Benchmark Setup Validation Run?

### 4. Search Lanes / Fan-Out

- What search lanes/templates exist per category?
- Are lanes hardcoded, generated dynamically, or selected by rules?
- For each category, what sources or SERP templates are currently used?
  - Google organic
  - Google News
  - Google Shopping
  - Google Videos
  - Google short-video verticals
  - `site:` operators
  - other search engines
  - datasets
  - platform-specific search
- How many results are collected per lane?
- Are lane results weighted differently before reranking?
- Can we see the raw candidate list per lane for sample runs?

### 5. Raw Candidate Pool

- For a given query, can we access:
  - source/search lane,
  - expanded query,
  - raw rank,
  - URL,
  - title,
  - snippet/description,
  - SERP metadata,
  - timestamp,
  - locale/country/language?
- How large is the raw candidate pool before dedupe?
- How large is it after dedupe?
- Are raw candidates stored anywhere after a run?

### 6. Deduplication

- Is there URL deduplication?
- Is there entity-level deduplication?
- Are canonical URLs normalized?
- How are duplicate URLs from multiple lanes handled?
- Can we see dedupe decisions in sample traces?
- Does dedupe happen before or after reranking?

### 7. Voyage Reranking

- Which Voyage model/version is used?
- Is reranking done once globally or separately per lane/category?
- What is the reranker input?
  - URL only?
  - title/snippet?
  - full content?
  - source metadata?
- What instruction or intent is passed to Voyage?
- Is the intent fixed by category, derived from user intent, or generated dynamically?
- Can we see:
  - reranker input candidates,
  - reranker scores,
  - final reranked order,
  - top-K cutoff?
- Are Voyage scores exposed in final output the actual reranker scores?

### 8. Top-K Selection

- How many results are selected after reranking before enrichment?
- Is top-K fixed globally or category-specific?
- Are there rules that force diversity across sources/search lanes?
- Are some sources preferred or penalized before enrichment?
- Can we see the top-K list before enrichment for sample runs?

### 9. Enrichment Routing

- How does the system decide whether a URL goes to:
  - WSAPI/platform scraper,
  - dataset,
  - Web Unlocker,
  - markdown scrape,
  - another method?
- Is routing rule-based, learned, or manually configured?
- Are routing rules category-specific?
- Which WSAPI/platform scrapers are available for each benchmark category?
- Which datasets are available for each benchmark category?
- Can we see enrichment route per URL in sample traces?

### 10. Enrichment Success, Failure, And Fallback

- What counts as enrichment success?
- What counts as enrichment failure?
- What fallback happens when WSAPI/platform scraper fails?
- When does Web Unlocker become the fallback?
- Are partial enrichments returned?
- Are errors stored?
- Are fallback decisions exposed in logs or traces?
- Can we see examples where enrichment succeeded and failed?

### 11. Middle Products / Debug Traces

- Can you provide 1-2 complete sample runs with middle products?
- For each sample run, can we get:
  - original query,
  - selected category,
  - expanded queries,
  - search lanes/templates,
  - raw SERP/search candidates,
  - dedupe decisions,
  - reranker input,
  - reranker scores/order,
  - top-K before enrichment,
  - enrichment route per URL,
  - enrichment success/failure,
  - fallback decisions,
  - final returned payload,
  - stage latencies,
  - errors?
- Can debug traces be enabled for the Diagnostic Benchmark Setup Validation Run?
- If full traces are not possible, which fields can be exposed?
- Are traces available through API, logs, files, dashboard, or backend export?

## P1 - Important Questions

These improve benchmark validity and scalability.

### 12. Existing Benchmarks / Golden Data

- Do we already have benchmark queries for any category?
- Do we already have golden labels or judged relevance data?
- Do we have previous nDCG, HFTE, or throughput measurements?
- Do we have known failure examples for current Discover?
- Are there categories where Discover is known to perform well or poorly?

### 13. Category Priorities

- Which category should we use for setup validation?
- Should we optimize for business priority or diagnostic value?
- Are `social_media_video`, `price_intelligence`, or `b2b_contact_data` preferred for the setup validation run?
- Are any categories blocked by access, legal, compliance, rate limits, or source reliability?

### 14. Same-Data Expectations

- For each category, what fields must a useful result contain?
- What fields are optional but valuable?
- What result types should be excluded?
- What is considered noise?
- What freshness is required?
- Are there fields that competitors must also return for a fair comparison?

### 15. HFTE Definition

- How should "Relevant Signal" be defined per category?
- Should HFTE count only structured fields, or also useful text snippets/content?
- Should missing required fields reduce the signal score?
- How should boilerplate, navigation, ads, duplicated content, and unrelated text be treated?
- Does Shahar already have a preferred HFTE formula?

### 16. Relevance Judging / nDCG@5

- Who should approve the relevance rubric?
- Should relevance grades be 0-3, 0-4, or another scale?
- Can LLM-assisted labels be used with human audit?
- What audit percentage is acceptable?
- Is there an expected agreement threshold before labels are trusted?
- Are there product-specific relevance rules we should encode?

### 17. Throughput And Latency

- What concurrency level matters for the benchmark?
- What timeout should count as failure?
- Should partial results count as success?
- Should retries be allowed?
- Should throughput be measured on final output only, or by stage?
- Are there rate limits or quotas we must account for?

### 18. Cost Constraints

- Should benchmark reports include API cost or internal cost?
- Are WSAPI/dataset/Web Unlocker routes materially different in cost?
- Are some sources too expensive for production use?
- Should architecture recommendations consider cost even if quality improves?

### 19. Compliance / Source Constraints

- Are there sources we should avoid or treat carefully?
- Are there restrictions around LinkedIn, TikTok, Instagram, YouTube, Crunchbase, or other platform data?
- For B2B contact data, are there compliance limits on profile/contact enrichment?
- Should reports distinguish "can retrieve" from "should rely on this source"?

## P2 - Optional / Upgraded Access Questions

These are valuable but should not block the readiness package unless Shahar says they are easy.

### 20. Internal Runnable Or Staging Access

- Is there a staging/internal endpoint where we can run Discover with debug output?
- Can we choose category explicitly in that environment?
- Can we choose or override search lanes?
- Can we test reranker intent variants?
- Can we test enrichment routing variants?
- Can we export raw candidates and traces from that environment?
- How much setup is required?

### 21. Architecture Variant Controls

- Which parts of the architecture can actually be changed for experiments?
  - expansion prompt/model,
  - category selection,
  - search lane templates,
  - raw candidate count,
  - dedupe rules,
  - Voyage intent,
  - reranker model/version,
  - top-K cutoff,
  - enrichment routing,
  - fallback rules,
  - output schema?
- Which changes require backend engineering?
- Which changes can be configured by a data scientist?
- Which changes are not possible now?

### 22. Trace Retention And Data Export

- Are traces retained after runs?
- For how long?
- Can traces be exported as JSON/CSV?
- Can traces include sensitive/internal fields?
- Are there privacy/security limits on what can be shared?
- Can setup validation traces be anonymized or redacted?

## Suggested Immediate Ask To Shahar

Hi Shahar,

To prepare the Discover API benchmark correctly, we need to understand the current architecture enough to run a Diagnostic Benchmark Setup Validation Run, not just a leaderboard.

Can you help with three things?

1. Confirm the current production pipeline: category selection, Gemini expansion, search-lane fan-out, Voyage reranking, and enrichment routing.

2. Provide 1-2 sample runs with middle products if possible:
   - original query,
   - selected category,
   - expanded queries,
   - search lanes/templates,
   - raw candidates,
   - dedupe decisions,
   - reranker input and output order,
   - top-K before enrichment,
   - enrichment route per URL,
   - fallback/errors,
   - final output,
   - stage timings.

3. Tell us whether debug traces can be enabled for the Diagnostic Benchmark Setup Validation Run.

If full debug traces are hard, even static sample traces would help us design the schemas, failure labels, and readiness gates correctly.

## Why These Questions Matter

If we only have final outputs, we can compute metrics like nDCG@5 and HFTE, but we will have weaker evidence about why a result is good or bad.

If we have middle products or traces, we can connect failures to pipeline stages:

- expansion,
- category routing,
- source/search lane,
- raw recall,
- dedupe,
- reranking,
- top-K selection,
- enrichment routing,
- extraction,
- fallback,
- schema,
- freshness,
- throughput.

That is what makes the benchmark useful for architecture decisions rather than just system ranking.
