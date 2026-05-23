# Task 1 - Gemini Flash 2.5 or gpt4o Expansion Prompt Evaluation

## Background

This document describes one scoped experiment inside the broader Discover API benchmark work. The broader work is about understanding and improving how Discover-style search handles different categories: a user query is expanded into better search queries, those queries are sent to a retrieval source such as Bright Data Google SERP, and the returned results are judged for whether they contain useful category-specific data.

This scoped task is intentionally narrower than the full benchmark. The full benchmark may eventually cover several P1 categories and source/tool choices, such as other business-data categories, social/video categories, price intelligence, WSAPI, datasets, or Discover API comparisons. This document only covers the `b2b_contact_data` category and only tests the query-expansion prompt step. The purpose is to find which expansion prompt produces downstream SERP results that are most useful for B2B contact-data discovery.

## What Shahar Asked

Shahar asked us to try different prompts for the query expansion step, using **Gemini Flash 2.5**, and see which prompt produces the most relevant results for the use case.

## Target Category

For now, Task 1 focuses only on:

```text
b2b_contact_data
```

We are not evaluating every P1 vertical yet. The first question is whether better Gemini Flash 2.5 expansion prompts can improve results for B2B contact-data discovery.

## Category Output Contract

Task 1 uses the B2B contact-data contract defined here:

```text
task/b2b_contact_data_category_output_contract.md
```

This contract defines what a useful B2B result means, including person fields, company fields, relevance grades, field coverage, evidence rules, and exclusions.

Without this contract, we can inspect expansion quality, but we cannot judge result usefulness consistently.

## Expansion Paradigms

Task 1 uses the B2B expansion paradigm map defined here:

```text
task/b2b_contact_data_expansion_paradigms.md
```

This map defines reusable expansion paradigms, parameter dimensions, structured expansion output, and candidate recipes.

The point is to avoid random prompt rewrites. Prompt variants should be built from explicit paradigm combinations.

## What This Means

This task is about testing the **query expansion step**.

Before searching, we take the original user query and ask Gemini Flash 2.5 to generate better search-query variants. We then compare different Gemini prompts to see which prompt creates expansions that lead to better downstream search results.

The variable being tested is:

> What prompt should we give Gemini Flash 2.5 so it expands the original query in the most useful way for this category/use case?

## What We Are Not Testing Here

This task is not primarily about:

- comparing Discover API to Tavily or Exa,
- testing WSAPI versus datasets,
- testing enrichment routing,
- testing different Bright Data tools,
- changing the final output schema,
- evaluating all architecture variants at once.

Those may come later. Task 1 isolates the expansion prompt.

## Example

Original query:

```text
heads of sales at US cybersecurity SaaS companies
```

### Expansion Prompt A - Broad Semantic Expansion

Could produce:

```text
cybersecurity SaaS sales leaders United States
VP sales cybersecurity software companies
heads of sales security SaaS company contacts
```

This prompt may improve recall but can also create broad/noisy searches that return company pages without usable contact details.

### Expansion Prompt B - Source-Aware Expansion

Could produce:

```text
site:linkedin.com/in "Head of Sales" cybersecurity SaaS
site:theorg.com cybersecurity SaaS sales leader
site:company.com team sales cybersecurity SaaS
```

This prompt may find more source-specific contact candidates, but it can over-depend on sources that are incomplete, blocked, or not consistently structured.

### Expansion Prompt C - Data-Field-Aware Expansion

Could produce:

```text
cybersecurity SaaS Head of Sales company title email LinkedIn
VP Sales security software company domain contact
sales leader cybersecurity SaaS name title company profile
```

This prompt may find results that contain more useful B2B contact-data fields, such as person name, company, title, company domain, professional profile URL, and contact hints.

## How To Evaluate Prompts Fairly

To compare expansion prompts fairly, keep the rest of the pipeline fixed.

Fixed inputs:

- same original query,
- same category/use case,
- same Gemini model: Gemini Flash 2.5,
- same number of expansions per prompt,
- same search/retrieval method after expansion,
- same result count,
- same locale/language settings,
- same scoring method.

Only change:

- the prompt given to Gemini Flash 2.5.

## What To Measure

For each expansion prompt, measure downstream result quality.

Possible measures:

- relevance of top results,
- number of useful results found,
- whether results match the category intent,
- whether results contain the fields required by the Category Output Contract,
- how much junk/noise the expansions introduce,
- whether expansions produce source-specific useful queries,
- whether expansions over-constrain and miss good results.

## Expected Output

For each tested prompt, record:

- prompt name/version,
- original query,
- generated expansions,
- search method used after expansion,
- returned results,
- relevance labels or qualitative judgment,
- useful fields found,
- failure notes,
- final recommendation.

## Success Criteria

This task succeeds when we can say:

- which expansion prompt produced the best downstream results,
- which prompt produced noisy or weak expansions,
- which prompt should be used for this category/use case,
- what prompt changes should be tested next.

## Important Interpretation

The expansions themselves are not the final deliverable.

The important question is:

> Which Gemini Flash 2.5 expansion prompt leads to the most relevant and useful search results after downstream retrieval?

So we judge prompts by downstream search quality, not only by whether the generated expansion queries look good.
