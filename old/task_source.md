Discover API: Category Architecture & Strategy (For Data Science Review)

 
The Pipeline Architecture:
 
1. Semantic Expansion (Gemini): Expands the user's query into 2-3 semantic variations.
2. Hardcoded Fan-out (SERP): Multiplies the expanded queries against category-specific SERP templates (e.g., Google Video, Google Shopping, specific site: operators).
3. Relevance Ranking (Voyage): Reranks candidates using a fixed, category-specific instruction-following intent.
4. Enrichment (WSAPI Collect): Routes the top-K URLs to Bright Data's platform-specific scrapers (for JSON data) or Web Unlocker (for Markdown).
 
 
1. Category: b2b_contact_data 🟠 (High Priority)

ICP: AI sales development representatives (SDRs), lead generation platforms, talent mapping, CRM enrichment tools.
Goal: Discover and enrich professional profiles, work history, and company firmographics (headcount, funding, industry) to build B2B contact lists.
 
Technical Recommendation:
 
● Search Strategy: Leverage Google's indexing of public professional networks.
● People: site:linkedin.com/in/ + site:crunchbase.com/person/.
● Companies: site:linkedin.com/company/ + site:crunchbase.com/organization/.
● Voyage Reranker Intent: "Prioritize professional profile pages and company pages. Focus on individuals with job titles, tenure, and skills. For companies, focus on headcount, industry, and funding. Strictly exclude job postings (/jobs/), career advice blogs, and HR software marketing pages."
● Extraction Strategy:
● Route to WSAPI Collect (LinkedIn Person Profile, LinkedIn Company, Crunchbase).
● Note: LinkedIn heavily blocks standard scraping. WSAPI is mandatory here to extract structured work history and education.
 
 
2. Category: price_intelligence 🟠 (High Priority)

ICP: Dynamic pricing engines, competitive analysis platforms, retail aggregators, supply chain AI.
Goal: Monitor product pricing, stock availability, discounts, and customer reviews across major e-commerce platforms in real-time.
 
Technical Recommendation:
 
● Search Strategy: Combine Google's dedicated shopping index with direct product detail page (PDP) targeting.
● Broad/Comparison: udm=28 (Google Shopping - provides cross-retailer comparison).
● Targeted: site:amazon.com/dp/, site:walmart.com/ip/.
● Voyage Reranker Intent: "Prioritize individual product detail pages (PDPs) with visible pricing data, discounts, availability, and seller info from major retailers. Strictly exclude coupon aggregators (RetailMeNot), affiliate review blogs ('Best X of 2026'), and price tracking tool pages."
● Extraction Strategy:
● Route to WSAPI Collect (Amazon, Walmart, Best Buy, eBay scrapers). This replaces a messy markdown scrape with 220+ structured fields (price, original price, SKU, ratings, variations) with zero parsing required.
 
 
 
3. Category: social_media_video 🟠 (High Priority)

ICP: Social listening platforms, brand monitoring AI, trend prediction models, AI marketing agents.
Goal: Discover trending/viral video content across major platforms, analyze engagement velocity, and access video metadata (captions, transcripts, hashtags) for NLP and sentiment analysis.
 
Technical Recommendation:
 
● Search Strategy: Use Google's video verticals for rich initial metadata (thumbnails, duration, platform source), supplemented by site: operators for platform guarantees.
● Short-form: udm=39 (Google Shorts - catches TikTok, Reels, YT Shorts) + site:tiktok.com.
● Long-form: tbm=vid (Google Videos) + site:youtube.com/watch.
● Voyage Reranker Intent: "Prioritize actual video content pages on TikTok, YouTube, and Instagram. Prefer videos with high engagement signals (views, likes) and original creator content. Strictly exclude text articles about social media, tool reviews, Spotify playlists, and compilation pages."
● Extraction Strategy:
● Crucial Note: Web Unlocker scrape_as_markdown fails on TikTok/YT/IG due to JS/anti-bot.
● Route URLs to WSAPI Collect: YouTube Videos Scraper, TikTok Posts Scraper, Instagram Reels Scraper. This yields exact views, likes, comments, and transcripts.
 
 
 
4. Category: job_market 🟡 (Medium Priority)

ICP: Labor market analytics firms, HR tech, automated recruiting AI, salary benchmarking models.
Goal: Aggregate active job listings, triangulate compensation data, and monitor required skills and hiring velocity across industries.
 
Technical Recommendation:
 
● Search Strategy: Google Jobs is the ultimate meta-aggregator.
● Listings: ibp=htl;jobs (Google Jobs vertical - aggregates Indeed, LinkedIn, Glassdoor, and company career pages in one search).
● Salaries/Companies: site:levels.fyi, site:glassdoor.com/Salaries.
● Voyage Reranker Intent: "Prioritize active job listing pages with structured data: job title, hiring company, salary range, location, and requirements. Strictly exclude resume writing tips, staffing agency marketing, 'how to interview' guides, and recruiter profiles."
● Extraction Strategy:
● Route to WSAPI Collect for Indeed, LinkedIn Jobs, and Glassdoor URLs. Use Web Unlocker for direct company career pages (e.g., Greenhouse, Lever).
 
 
5. Category: news_media 🟡 (Medium Priority)

ICP: PR monitoring tools, financial sentiment trading algos, media intelligence, risk intelligence. Goal: Track breaking news, narrative development, and public sentiment across global, localized, or industry-specific journalistic sources.
 
Technical Recommendation:
 
● Search Strategy: Google News dominates this vertical.
● Discovery: tbm=nws (Google News).
● Recency Filtering: Use tbs=qdr:h (past hour) or tbs=qdr:d (past day).
● Voyage Reranker Intent: "Prioritize primary-source news articles from established news organizations with editorial standards. Focus on substantive articles with datelines and bylines. Strictly exclude PR distribution sites (BusinessWire), opinion columns, aggregator landing pages, and paywalled pages with no body text."
● Extraction Strategy:
● Because news lives on 50,000+ different domains, Web Unlocker (scrape_as_markdown) is the primary engine here.
● Use WSAPI Collect only for specific supported giants (BBC, CNN, NYT).
 
 
6. Category: real_estate ⚪ (Lower/Niche Priority)

ICP: PropTech startups, Automated Valuation Models (AVMs), real estate investment trusts (REITs). Goal: Aggregate property listings, historical price data, tax history, and agent data for market valuation and investment signals.
 
Technical Recommendation:
 
● Search Strategy: Target the massive MLS aggregators.
● Queries: site:zillow.com/homedetails/, site:redfin.com, site:realtor.com/realestateandhomes-detail/.
● Voyage Reranker Intent: "Prioritize individual property listing pages (PDPs) with listing price, square footage, beds/baths, lot size, and status. Strictly exclude mortgage calculators, home improvement blogs, agent marketing pages, and neighborhood overview pages without specific property data."
● Extraction Strategy:
● Route to WSAPI Collect (Zillow Properties Scraper, Airbnb, Booking). Zillow scraping yields massive structured objects (price history, tax records, comparables) that markdown parsing cannot cleanly replicate.
 
 
7. Category: financial_data ⚪ (Lower/Niche Priority)

ICP: Quant hedge funds, equity research analysts, macroeconomic forecasting AI. Goal: Source regulatory filings (SEC), earnings transcripts, and alternative data signals (hiring velocity, employee sentiment) for financial modeling.
 
Technical Recommendation:
 
● Search Strategy: Extremely precise site: and filetype: operators.
● Filings: site:sec.gov/cgi-bin/browse-edgar 10-K OR 10-Q OR 8-K.
● Presentations: filetype:pdf "earnings call" OR "investor presentation".
● Alt Data: site:indeed.com hiring (hiring velocity).
● Voyage Reranker Intent: "Prioritize SEC filings, earnings call transcripts, official investor presentations, and structured financial metrics. Prefer court-defensible data provenance. Strictly exclude retail investor forums (WallStreetBets), crypto speculation, stock tip newsletters, and financial advisor marketing."
● Extraction Strategy:
● Web Unlocker is primary for SEC.gov and PDF extraction.
● Route to WSAPI Collect for Yahoo Finance (stock data) and Indeed/Glassdoor (alternative signals).
 
 
🧪 Instructions for the Data Scientist:
1. Benchmark the SERP Verticals: Run A/B tests comparing site:tiktok.com (organic results) against udm=39 (Google short videos). Evaluate the payload (Does udm=39 reliably return the duration and thumbnail JSON nodes?).
2. Tune the Reranker Intent: Take the intents provided above and run them through the Voyage rerank-2.5 API against a static dataset of 100 mixed URLs (50 good, 50 noise). Measure the NDCG@10 lift. The instruction-following capability of Voyage 2.5 is highly sensitive to the EXCLUDE: clauses.
3. Evaluate the "Enrichment" Fallback Rate: Test the routing logic. If the top 20 results for social_media_video yield 15 YouTube/TikTok links and 5 blog links, verify that the 15 are successfully parsed by WSAPI Collect and the 5 fallback correctly to Web Unlocker.
 