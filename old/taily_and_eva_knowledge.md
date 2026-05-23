# Tavily And Exa Knowledge

## Naming Note

The benchmark task mentions **Tavily** and **Exa**.

The filename says `taily_and_eva` because that is how the note was requested, but the actual products are:

- **Tavily**
- **Exa**

## Why These Matter For This Benchmark

Tavily and Exa are external AI-search APIs. Shahar wants Discover API compared against them because they are alternative ways to search the web and return LLM-ready results.

In plain terms:

- **Discover API** is Bright Data's own search/discovery system.
- **Tavily** is an external search API built for AI/LLM apps.
- **Exa** is an external search API built for AI/LLM apps, with strong semantic search and content retrieval features.

The benchmark should not treat Tavily or Exa as architecture variants of Discover. They are competitor/baseline systems.

## What Is Tavily?

Tavily is a web search API designed for developers and AI applications.

Its Search API executes a query and returns ranked web results. Tavily can also return answer text, snippets/content, raw extracted page content, images, favicon URLs, response time, usage/credits, and request IDs depending on settings.

Official docs:

- Tavily Search API: https://tavilyai.mintlify.app/documentation/api-reference/endpoint/search
- Tavily Extract API: https://docs.tavily.com/documentation/api-reference/endpoint/extract

### Tavily Search - Important Knobs

These are the settings that matter for fair comparison later:

| Setting | What It Controls | Why It Matters |
|---|---|---|
| `query` | The search query | Must match the same benchmark query used for Discover and Exa. |
| `search_depth` | Latency/relevance tradeoff | `basic`, `fast`, `ultra-fast`, and `advanced` have different quality, latency, and credit costs. |
| `chunks_per_source` | Number of short snippets per source for advanced search | Affects content length and HFTE token cost. |
| `max_results` | Maximum results returned | Must be normalized against Discover and Exa. Tavily docs show max 20. |
| `topic` | Search topic | Options include `general`, `news`, and `finance`; this can affect category fairness. |
| `time_range`, `start_date`, `end_date` | Freshness filtering | Important for news, jobs, prices, and fast-changing data. |
| `include_answer` | Whether Tavily returns an LLM-generated answer | Usually should be off for result-list comparison unless all systems return comparable answers. |
| `include_raw_content` | Whether Tavily returns parsed page content | Important for HFTE, but increases payload and latency. |
| `include_images` | Whether image results are returned | Could matter for video/product pages but may not be comparable. |
| `include_domains` / `exclude_domains` | Domain filters | Important for site-specific tests, but must be applied consistently. |
| `country` | Country boost for general search | Must match locale settings in Discover/Exa. |
| `auto_parameters` | Tavily auto-selects parameters | Should likely be disabled for controlled benchmarks unless explicitly testing Tavily auto mode. |
| `include_usage` | Returns credit usage | Useful for cost reporting. |

### Tavily Extract - Important Knobs

Tavily Extract takes one or more URLs and extracts page content.

It matters because Tavily Search can find URLs, while Extract can act like an enrichment/content retrieval step.

Important settings:

| Setting | What It Controls | Why It Matters |
|---|---|---|
| `urls` | URL or list of URLs to extract | Equivalent to an enrichment step after search. |
| `extract_depth` | Extraction depth | `basic` is cheaper/faster; `advanced` retrieves more data and may handle complex pages better. |
| `format` | `markdown` or `text` | Affects token count and HFTE. |
| `timeout` | Extraction timeout | Must be normalized for throughput/failure measurement. |
| `include_images` | Returns extracted images | Usually off unless the category needs images. |
| `query` + `chunks_per_source` | Query-focused extracted chunks | Could reduce tokens, but changes comparability if Discover returns full content. |
| `include_usage` | Returns credit usage | Useful for cost reporting. |

## What Is Exa?

Exa is a search engine/API built for AI systems. It focuses on finding web content semantically and returning LLM-ready page content or highlights.

Exa supports search, contents retrieval, structured output, and several search types with different speed/quality tradeoffs.

Official docs:

- Exa Search API: https://exa.ai/docs/reference/search
- Exa Search API guide: https://exa.ai/docs/reference/search-api-guide
- Exa Contents API: https://exa.ai/docs/reference/contents-api-guide

### Exa Search - Important Knobs

These are the settings that matter for fair comparison later:

| Setting | What It Controls | Why It Matters |
|---|---|---|
| `query` | Search query | Must match Discover/Tavily query. |
| `type` | Search mode | Options include `auto`, `instant`, `fast`, `neural`, `deep-lite`, `deep`, and `deep-reasoning`; they vary in latency and depth. |
| `category` | Data category focus | Options include `company`, `people`, `research paper`, `news`, `personal site`, and `financial report`. Useful for B2B, news, and financial categories. |
| `numResults` | Number of results returned | Must be normalized against Discover/Tavily. Exa docs show default 10 and max 100 for several search types. |
| `includeDomains` / `excludeDomains` | Domain filters | Useful for site-specific tests; category-specific restrictions apply. |
| `startPublishedDate` / `endPublishedDate` | Publication date filtering | Important for news, finance, jobs, and freshness-sensitive categories. |
| `startCrawlDate` / `endCrawlDate` | Crawl-date filtering | Helps control recency from Exa's index perspective. |
| `userLocation` | User country/location | Must align with locale settings. |
| `contents` | Whether returned URLs include content/highlights/summary | Strongly affects token cost, HFTE, and output comparability. |
| `outputSchema` | Structured output from search | Powerful, but may make Exa output not directly comparable to Discover unless we intentionally evaluate structured extraction. |
| `systemPrompt` | Instructions for synthesized output/deep search | Useful but should be controlled carefully to avoid giving Exa extra task-specific advantage. |

### Exa Contents - Important Knobs

Exa Contents retrieves clean content from URLs. Exa says Contents can return text, highlights, summaries, and subpage crawling.

Important settings:

| Setting | What It Controls | Why It Matters |
|---|---|---|
| `urls` | URLs to retrieve content for | Equivalent to enrichment after search. |
| `text` | Full page content as markdown | Good for full content, but increases token cost. |
| `highlights` | Relevant excerpts | Token-efficient; useful for LLM workflows but may not match Discover output style. |
| `summary` | LLM-generated summary | Useful, but not equivalent to raw extraction. |
| `subpages` / `subpageTarget` | Crawl linked pages under a site | Powerful, but likely unfair unless other systems get the same capability. |
| `maxAgeHours` | Cache/freshness control | Important for prices, news, jobs, and other freshness-sensitive categories. |

## Key Difference Between Tavily And Exa

Very roughly:

- **Tavily** feels like an AI-search API that returns ranked web results, snippets, optional answers, and optional raw content/extraction.
- **Exa** feels like a semantic AI-search/content API with many search modes, content/highlight retrieval, categories like people/company/news/financial reports, and structured output options.

That rough distinction is enough for now. For the benchmark, the exact API settings matter more than the marketing category.

## Why Fair-Run Settings Matter

If we compare Discover, Tavily, and Exa with different settings, the benchmark can become unfair.

Examples:

- If Exa returns full text but Discover returns only snippets, Exa may have more useful signal and more tokens.
- If Tavily `advanced` search is used but Exa `instant` is used, the latency/quality tradeoff is not comparable.
- If Tavily includes an LLM-generated answer and Discover only returns links, the output shape is different.
- If Exa uses `deep` search with structured output and Discover uses plain search, Exa gets extra reasoning/extraction help.
- If one system gets 20 results and another gets 5, nDCG@5 can still be computed, but candidate recall and enrichment opportunity differ.

So we need to decide fair settings before running a real benchmark.

## First Fair-Run Hypothesis

This is not final. It is a starting hypothesis to investigate later.

For a first comparable run, consider:

### Tavily

- `search_depth`: `basic` or `advanced`, but choose one and keep it fixed.
- `max_results`: same target as Discover and Exa, likely 10 or 20.
- `topic`: `general` by default, `news` for news category, maybe `finance` for financial category.
- `include_answer`: false for result-list comparison.
- `include_raw_content`: false for ranking-only comparison; true/markdown for content/HFTE comparison if Discover also returns content.
- `include_usage`: true if cost reporting is needed.
- `auto_parameters`: false for controlled tests, unless explicitly testing Tavily auto mode.

### Exa

- `type`: `auto` or `fast` for general comparable search; avoid `deep` until we intentionally test deep/research mode.
- `numResults`: same target as Discover and Tavily, likely 10 or 20.
- `category`: only use if the category maps cleanly, such as `people`, `company`, `news`, or `financial report`.
- `contents.highlights`: possible token-efficient content mode.
- `contents.text`: only if full content is needed and token cost is controlled.
- `outputSchema`: probably off for baseline result-list comparison; maybe on for a separate structured-output variant.

## What We Still Need To Research Later

Before finalizing fair-run settings, we still need to check:

- Tavily current pricing/credit rules for search and extract.
- Exa current pricing/cost behavior for search, contents, deep search, and content retrieval.
- Rate limits for both APIs.
- Exact SDK parameter names in Python.
- Whether Tavily/Exa support the needed locale/country controls for each category.
- Whether Tavily/Exa handle platform-heavy sources like TikTok, Instagram, LinkedIn, Amazon, Zillow, and SEC PDFs well enough.
- Whether we compare only search results, or search-plus-content, or separate both as different benchmark modes.

## Sources Checked

- Tavily Search API docs: https://tavilyai.mintlify.app/documentation/api-reference/endpoint/search
- Tavily Extract API docs: https://docs.tavily.com/documentation/api-reference/endpoint/extract
- Exa Search API docs: https://exa.ai/docs/reference/search
- Exa Search API guide: https://exa.ai/docs/reference/search-api-guide
- Exa Contents API guide: https://exa.ai/docs/reference/contents-api-guide
