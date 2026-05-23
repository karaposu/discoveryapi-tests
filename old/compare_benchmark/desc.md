# Discover API External Baseline Evaluation

## Purpose

This document explains the idea of comparing **current Discover API** with external search/API products such as **Tavily** and **Exa**.

This is the first evaluation layer because it is non-invasive.

Non-invasive means:

- no backend code changes,
- no internal Discover traces required,
- no architecture variant controls required,
- no need to inspect Gemini, Voyage, SERP fan-out, or enrichment routing yet,
- only final outputs from each system are compared.

The goal is to answer:

> For a chosen category and query set, does current Discover API produce better or worse final outputs than Tavily and Exa?

## Systems Compared

| System | Role In Evaluation |
|---|---|
| Discover API | Bright Data system being evaluated |
| Tavily | External AI/web search baseline |
| Exa | External AI/web search baseline |

Tavily and Exa are not internal Discover components. They are external products used as comparison baselines.

## What This Evaluation Can Answer

This comparison can answer:

- Does Discover produce more relevant top results than Tavily/Exa?
- Does Discover return more useful category-specific information?
- Does Discover return less junk text per useful fact?
- Is Discover faster or slower under comparable settings?
- Which categories look strong or weak from the outside?
- Is deeper internal architecture diagnosis worth prioritizing for a category?

Example:

If Discover performs worse than Exa for `price_intelligence`, we know there is a competitiveness gap. That does not yet tell us exactly whether the gap is caused by source choice, reranking, enrichment, or output schema.

## What This Evaluation Cannot Answer

This comparison cannot confidently answer:

- whether Gemini query expansion failed,
- whether SERP/search-lane fan-out failed,
- whether raw candidate recall was weak,
- whether dedupe removed good results,
- whether Voyage reranking made the wrong choice,
- whether enrichment routing failed,
- whether Web Unlocker or WSAPI extraction failed internally,
- which architecture change will fix Discover.

Those require internal traces, middle products, or variant controls.

So this evaluation can tell us **whether Discover is competitive externally**. It cannot fully explain **why Discover succeeds or fails internally**.

## Required Setup Before Running

Even though this evaluation is non-invasive, it still needs a proper Diagnostic Benchmark Setup.

Minimum required setup:

- choose setup validation category,
- create setup validation query set,
- define Category Output Contract,
- define relevance rubric,
- define judging workflow,
- define human audit process,
- define metric formulas,
- define fair-run settings for Discover, Tavily, and Exa,
- define raw and normalized output storage.

Without these, the comparison may produce numbers that are not trustworthy.

## Evaluation Flow

```text
same query set
  -> Discover API final outputs
  -> Tavily final outputs
  -> Exa final outputs
  -> normalize outputs
  -> pool and dedupe results
  -> LLM-assisted judging + human audit
  -> compute metrics
  -> compare systems
```

## Metrics

Use a small metric set first.

### 1. nDCG@5

Purpose:

- Measures ranking quality for the top 5 results.

Needs:

- external relevance labels,
- relevance rubric,
- final result order from each system.

Answers:

> Did the system put the best results near the top?

Notes:

- Do not use Discover/Voyage relevance scores as ground truth.
- Labels should come from LLM-assisted judging plus human audit.

### 2. Category Output Contract Coverage

Purpose:

- Measures whether the output contains the required useful fields for the category.

Example for `price_intelligence`:

- product name,
- product URL,
- seller/retailer,
- current price,
- currency,
- availability,
- rating/review count,
- freshness/timestamp.

Answers:

> Did the system return the data the category actually needs?

This is a custom benchmark metric.

### 3. HFTE

Purpose:

- Measures useful information per token.

Simple starting definition:

```text
HFTE = useful_field_score / total_output_tokens
```

Where `useful_field_score` comes from the Category Output Contract.

Answers:

> How dense is the useful information in the returned output?

This is a custom metric and must be defined per category.

### 4. Latency And Success Rate

Purpose:

- Measures whether each system returns usable results reliably.

Possible fields:

- request duration,
- timeout count,
- error count,
- number of usable results returned,
- partial success flag.

Answers:

> Did the system return enough usable results within the allowed time?

Throughput/concurrency can be added later after the basic comparison works.

## Fair-Run Rules

The comparison is only fair if systems are run under comparable conditions.

We need to control:

- same query set,
- same category intent,
- same locale/country/language where possible,
- same result count target,
- similar timeout,
- similar content depth,
- consistent retry policy,
- consistent freshness filters where relevant,
- no extra generated answer unless every system is evaluated in answer mode.

Important:

If Tavily or Exa returns full page content and Discover returns only snippets, HFTE and output coverage are not directly comparable unless we define that mode intentionally.

## Output Modes

We may need two comparison modes.

### Mode A: Ranking-Only Comparison

Compare only ranked result lists:

- URL,
- title,
- snippet/description,
- rank/order.

Main metric:

- nDCG@5.

Use this to evaluate search/ranking quality.

### Mode B: Search-Plus-Content Comparison

Compare ranked results plus returned content or structured fields.

Main metrics:

- nDCG@5,
- Category Output Contract coverage,
- HFTE,
- latency/success rate.

Use this to evaluate final usefulness for LLM/data workflows.

## How This Fits Into The Larger Evaluation

The full evaluation should be layered:

### Layer 1: External Baseline Evaluation

Compare:

- current Discover API,
- Tavily,
- Exa.

Evidence:

- final outputs only.

Goal:

- determine whether Discover is competitive externally.

### Layer 2: Diagnostic Failure Attribution

Add:

- internal traces,
- middle products,
- static examples,
- stage evidence.

Goal:

- explain where Discover succeeds or fails internally.

### Layer 3: Architecture Variant Evaluation

Add:

- controllable Discover variants,
- source/search-lane changes,
- reranker intent changes,
- enrichment routing changes,
- fallback/schema changes.

Goal:

- test which architecture changes improve Discover.

## Recommended First Step

Start with **Layer 1: External Baseline Evaluation**.

It is the fastest useful comparison because it does not require backend access.

But do not treat Layer 1 as the full answer. If Discover loses or wins, we still need Layer 2 to explain why.

## Main Risk

The main risk is over-interpreting final-output results.

Example:

If Discover returns worse top-5 results than Exa, we can say:

> Discover performed worse than Exa on this setup validation query set.

We should not immediately say:

> Discover's reranker failed.

That would require trace evidence or a controlled reranker variant.

## Summary

Comparing Discover API with Tavily and Exa is a good first evaluation layer.

It is useful because it is non-invasive and can show whether Discover is externally competitive.

It still requires metrics, labels, Category Output Contracts, and fair-run settings.

It cannot fully explain internal architecture causes without traces or middle products.
