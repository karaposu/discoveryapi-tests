# Task Elaboration

The task is to evaluate whether Bright Data's Discover API architecture can be improved for different search/use-case categories.

Here, "category" means a business use case or vertical, not a code category. Examples:

- `b2b_contact_data`: finding people and companies
- `price_intelligence`: finding products and prices
- `social_media_video`: finding TikTok, YouTube, and Instagram videos
- `job_market`: finding job listings
- `news_media`: finding news articles
- `real_estate`: finding property listings
- `financial_data`: finding filings, earnings documents, and finance data

"Subcategories" means the smaller search lanes inside each category.

For example, for `b2b_contact_data`, the subcategories are roughly:

- people profiles: LinkedIn profiles, Crunchbase people pages
- company profiles: LinkedIn company pages, Crunchbase organization pages

For `social_media_video`, the subcategories are:

- short videos: TikTok, Reels, YouTube Shorts
- long videos: YouTube watch pages

For `price_intelligence`, the subcategories are:

- broad shopping comparison: Google Shopping
- specific product pages: Amazon PDPs, Walmart PDPs, Best Buy pages, etc.

The current Discover API appears to work roughly like this:

1. User gives a query.
2. Gemini expands it into 2-3 related query variants.
3. The system knows the category, then fans out into hardcoded search templates/subcategories.
   Example templates include Google Shopping, `site:amazon.com/dp/`, `site:linkedin.com/in/`, `tbm=nws`, and similar vertical searches.
4. It takes about the first 20 results per subcategory/search lane.
5. It reranks all candidates with Voyage using an intent instruction.
6. It enriches the top URLs using WSAPI/platform scrapers if possible, otherwise Web Unlocker/markdown.

What Shahar is asking for:

For each category, benchmark whether this architecture is better than:

- Tavily
- Exa
- current Discover API
- new architecture variants we propose

A "new architecture variant" could mean changing:

- the search source: normal Google vs Google News vs Google Shopping vs Google Videos vs site-specific search
- the query expansion strategy
- the reranker intent text
- whether results go to Web Unlocker, WSAPI scrapers, datasets, or another enrichment source
- fallback rules when WSAPI cannot parse a URL

Expected deliverable per category:

- Run at least 50 queries for that category.
- Compare the systems.
- Report quality and efficiency.
- Then move to the next category without waiting.

The metrics to track:

- **HFTE**: how much useful/relevant information is returned per token. The goal is less junk HTML, ads, navigation, scripts, and boilerplate.
- **nDCG@5**: whether the best 5 results are actually the most relevant after reranking.
- **Throughput**: whether the system can do many parallel fetches quickly. This is less important, but still worth tracking.

In plain terms:

Shahar wants a category-by-category search architecture benchmark to decide how Discover API should search, rerank, and enrich results for each use case.
