# Setup Validation Category Selection With Diagnostic Value

## Purpose

This document explains how to choose the setup validation category for the Discover API benchmark.

The setup validation category should not be chosen only by business priority. The Diagnostic Benchmark Setup Validation Run's job is to test whether the **Diagnostic Benchmark Setup** works:

- Can we run systems under comparable settings?
- Can we define a category-specific **Category Output Contract**?
- Can we judge relevance with LLM-assisted labels plus human audit?
- Can we compute nDCG@5 and HFTE?
- Can we identify where failures happen in the pipeline?
- Can we use the result to design architecture variants?

So the best first category is the one that gives the strongest diagnostic signal with manageable access risk.

## Selection Criteria

| Criterion | What It Means | Why It Matters |
|---|---|---|
| Diagnostic value | The category exposes multiple failure modes across the pipeline | The setup validation run should teach us whether the benchmark can explain failures, not only produce scores. |
| Access feasibility | We can realistically run the needed sources/enrichments | A blocked category wastes the setup validation run. |
| Source diversity | The category uses multiple search lanes/sources | Tests whether source selection matters. |
| Enrichment difficulty | Results need WSAPI/datasets/Web Unlocker routing | Tests whether enrichment strategy affects HFTE and data usefulness. |
| Category Output Contract clarity | We can define required useful fields clearly | Needed for HFTE and fair comparison. |
| Judging clarity | A judge can tell good vs bad results reliably | Needed for nDCG@5 labels. |
| Failure attribution | Failures can be mapped to pipeline stages | Needed for architecture recommendations. |
| Business value | Shahar/product cares about the category | The setup validation result should matter. |
| Risk/compliance | Legal/platform/data risk is manageable | High-risk categories can stall. |

## Recommended First Choices

### Option 1: `social_media_video`

Recommended if the goal is maximum diagnostic value.

#### Why It Is Strong

`social_media_video` stresses many parts of the Discover architecture at once:

- search lane selection,
- Google Videos versus Google short-video vertical,
- `site:tiktok.com` and `site:youtube.com/watch`,
- platform-specific routing,
- JS/anti-bot enrichment problems,
- Web Unlocker versus WSAPI/platform scraper,
- engagement metadata extraction,
- captions/transcripts,
- Category Output Contract design,
- schema normalization across TikTok, YouTube, and Instagram.

This category is especially good for testing whether final-output metrics can be connected to architecture failures.

For example:

- If results are mostly articles about videos, the source/search lane is wrong.
- If results are real videos but missing views/likes/comments, enrichment is weak.
- If TikTok/Instagram pages fail as markdown, routing should use platform scrapers.
- If YouTube dominates and TikTok is missing, source coverage may be biased.
- If the model ranks tool reviews or playlists above original videos, reranking intent is weak.

#### Useful Category Output Contract

A useful social video result should ideally include:

- platform,
- video URL,
- creator/channel,
- title or caption,
- topic match,
- publish date if available,
- views or engagement count if available,
- likes/comments/shares if available,
- transcript, caption, or description if available.

This is a good Category Output Contract for setup validation because it is concrete but not trivial.

#### Why It Helps Benchmark Design

It reveals whether the benchmark can handle:

- multi-platform results,
- source-specific enrichment,
- missing metadata,
- token-heavy markdown,
- structured versus unstructured content,
- platform access failures.

#### Risks

- TikTok, Instagram, and YouTube can be hard to enrich through generic markdown.
- Engagement metadata may be unavailable or stale.
- Platform access can be unstable.
- Category Output Contract differs by platform.

These risks are exactly why the category is diagnostically useful, but they also mean we should confirm with Shahar that access is feasible.

#### Verdict

Best setup validation choice if Shahar confirms platform access and wants a category that stresses the whole pipeline.

## Option 2: `price_intelligence`

Recommended if the goal is structured-data clarity and lower platform/social risk.

### Why It Is Strong

`price_intelligence` is also a very strong setup validation category because it stresses:

- Google Shopping versus product detail pages,
- broad comparison pages versus retailer PDPs,
- Amazon/Walmart/Best Buy/eBay enrichment,
- structured field extraction,
- freshness,
- product deduplication,
- seller/availability normalization,
- HFTE as useful structured data per token.

This category is good because the Category Output Contract is easier to define than social video.

For example:

- If results are affiliate blogs, source/reranker intent is wrong.
- If results are product pages but price/availability are missing, enrichment is weak.
- If Google Shopping gives offers but Amazon PDP gives product detail, output normalization is the challenge.
- If prices are stale, freshness becomes a benchmark failure.
- If duplicate products consume top-K slots, dedupe/entity normalization is weak.

### Useful Category Output Contract

A useful price intelligence result should ideally include:

- product name,
- product URL,
- seller/retailer,
- current price,
- currency,
- availability or stock status,
- rating/review count if available,
- discount/original price if available,
- SKU/model/variant if available,
- timestamp or freshness signal.

This contract is concrete and maps well to HFTE because useful signal is structured.

### Why It Helps Benchmark Design

It reveals whether the benchmark can handle:

- structured product data,
- freshness-sensitive information,
- product/entity dedupe,
- retailer-specific enrichment,
- comparison between search sources and product pages,
- token efficiency in structured outputs.

### Risks

- Prices can change quickly.
- Product matching across retailers is hard.
- Google Shopping output and retailer PDP output are not identical.
- Some retailer pages may require specialized scrapers.

These risks are manageable and useful for setup validation.

### Verdict

Best setup validation choice if Shahar wants a category with clearer structured data and probably easier judging than social video.

## Weaker Setup Validation Choices

These categories may still be important later. They are weaker as the setup validation category because they either create access/compliance risk, have less diagnostic spread, or make judging/ground truth harder too early.

### `b2b_contact_data`

#### Why It Is Important

This is high business value. It maps to lead generation, CRM enrichment, and professional/company discovery.

#### Why It Is Weaker For Setup Validation

- LinkedIn and Crunchbase access may be constrained.
- Profile/contact data has more compliance and platform-policy risk.
- It may require internal WSAPI routes that are not easily available.
- Judging relevance can involve sensitive distinctions: person profile versus company page versus job page versus HR content.
- "Good result" may depend heavily on ICP details.

#### What It Would Test Well

- profile/company source routing,
- LinkedIn/Crunchbase enrichment,
- exclusion of job posts and career advice,
- company/person schema quality.

#### Verdict

Good later category. Risky setup validation choice unless Shahar explicitly says this is top priority and access/compliance are already handled.

### `job_market`

#### Why It Is Important

It maps to active job listings, salary signals, hiring velocity, and labor market analytics.

#### Why It Is Weaker For Setup Validation

- Active job freshness is hard.
- Google Jobs vertical availability needs confirmation.
- Duplicate listings across Indeed, LinkedIn, Glassdoor, and company ATS pages are common.
- Salary is often missing.
- Expired postings can pollute results.
- ATS pages have inconsistent structures.

#### What It Would Test Well

- freshness,
- dedupe,
- job schema extraction,
- source selection between meta-aggregators and direct job pages.

#### Verdict

Useful later. Not the best setup validation choice because stale/duplicate/expired job problems can make benchmark design harder before we validate the basic setup.

### `news_media`

#### Why It Is Important

It maps to media monitoring, risk intelligence, sentiment tracking, and breaking-news use cases.

#### Why It Is Weaker For Setup Validation

- News relevance depends heavily on freshness windows.
- Many pages are paywalled or partially accessible.
- Google News and recency parameters need careful setup.
- PR wires, opinion pieces, aggregators, and syndicated content create judging ambiguity.
- News is broad across many domains, so source-specific enrichment is less clean.

#### What It Would Test Well

- recency,
- Web Unlocker extraction,
- freshness filters,
- source credibility,
- news-body extraction.

#### Verdict

Good for freshness testing later. Weaker setup validation choice because it may become a recency/paywall/source-credibility benchmark before we validate core mechanics.

### `real_estate`

#### Why It Is Important

It maps to property listings, valuation, property facts, historical price, and market intelligence.

#### Why It Is Weaker For Setup Validation

- Lower/niche priority in the task source.
- Regional source coverage can dominate the benchmark.
- Property status and pricing can be stale.
- Zillow/Redfin/Realtor support needs confirmation.
- Category Output Contract may vary by country/source.

#### What It Would Test Well

- structured property enrichment,
- price history,
- listing status,
- source-specific scraper routing.

#### Verdict

Good later if real estate becomes priority. Not the best setup validation choice because it is lower priority and may depend heavily on regional source availability.

### `financial_data`

#### Why It Is Important

It maps to filings, earnings transcripts, investor presentations, and alternative data.

#### Why It Is Weaker For Setup Validation

- Lower/niche priority in the task source.
- PDF and filing extraction can become its own benchmark problem.
- Relevance requires domain-specific financial judgment.
- Official filings, investor pages, Yahoo Finance, and alternative signals are very different data types.
- The benchmark can become about document parsing rather than Discover architecture.

#### What It Would Test Well

- SEC/official-source targeting,
- PDF extraction,
- financial source credibility,
- structured finance data.

#### Verdict

Good later for document/finance-specific architecture. Not the best setup validation choice because it can overfocus on PDF/document extraction and domain-specific judgment.

## Comparison Table

Scores are qualitative: 1 = weak, 5 = strong.

| Category | Diagnostic value | Access feasibility | Category Output Contract clarity | Judging clarity | Risk level | Setup validation fit |
|---|---:|---:|---:|---:|---:|---:|
| `social_media_video` | 5 | 3 | 4 | 4 | 4 | 5 |
| `price_intelligence` | 5 | 4 | 5 | 4 | 3 | 5 |
| `b2b_contact_data` | 4 | 2 | 3 | 3 | 5 | 2 |
| `job_market` | 4 | 3 | 4 | 3 | 3 | 3 |
| `news_media` | 3 | 4 | 3 | 3 | 3 | 3 |
| `real_estate` | 3 | 3 | 4 | 4 | 3 | 2 |
| `financial_data` | 3 | 3 | 3 | 2 | 3 | 2 |

Important:
- High risk does not mean bad category.
- High risk means it may be bad as the **setup validation category** because it can slow benchmark validation.

## Recommendation

Default recommendation:

1. Choose **`social_media_video`** if Shahar confirms platform access and wants the strongest architecture-diagnostic setup validation run.
2. Choose **`price_intelligence`** if Shahar wants clearer structured fields, easier judging, and fewer platform/social access risks.

If Shahar does not have a strong preference, start with **`social_media_video`** because it stresses the widest range of Discover pipeline stages.

If Shahar is worried about access, freshness of engagement metrics, or platform restrictions, start with **`price_intelligence`**.

## What To Ask Shahar

Before locking the setup validation category, ask:

- Which category matters most right now from a product/business perspective?
- For `social_media_video`, can we reliably enrich TikTok, YouTube, and Instagram URLs?
- For `price_intelligence`, can we reliably enrich Amazon, Walmart, Best Buy, eBay, and Google Shopping results?
- Are any of these categories blocked by compliance, cost, access, or rate limits?
- Which category has existing traces, known failures, or sample runs?
- Which category would produce the most useful architecture decision after a 10-query setup validation run?

## Final Decision Rule

Pick the setup validation category using this rule:

1. It must be feasible to run with available sources/enrichment.
2. It must expose multiple pipeline failure modes.
3. It must have a clear Category Output Contract.
4. It must be judgeable by LLM-assisted labels plus human audit.
5. It must matter enough to Shahar that the setup validation result is useful.

Under this rule, the strongest setup validation choices are **`social_media_video`** and **`price_intelligence`**.
