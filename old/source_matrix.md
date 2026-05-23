# Discover API Candidate Source / Enrichment Matrix

## Purpose

This matrix maps each benchmark category to candidate search sources and enrichment routes.

This is a **draft candidate matrix**, not a statement of current production Discover routing.

Use it to:

- see what sources and enrichments look plausible,
- ask Shahar better architecture questions,
- design setup validation hypotheses,
- identify expected useful fields,
- mark access, quality, compliance, and freshness risks.

## Evidence And Status Legend

### Evidence

- `task_source`: mentioned or implied in `task/task_source.md`.
- `local_sdk`: visible in the local SDK/repo inventory.
- `inferred`: reasonable candidate based on category needs, but not directly confirmed.
- `shahar_confirmed`: confirmed by Shahar/backend.
- `setup_validation_observed`: observed in actual setup validation output or traces.

### Confidence

- `high`: directly supported by task source or local SDK and clearly fits the category.
- `medium`: plausible but needs Shahar or setup validation confirmation.
- `low`: speculative, or usefulness depends heavily on access/details.

### Production Status

- `unknown`: not confirmed in production Discover.
- `confirmed`: Shahar/backend or traces confirm production use.
- `not_used`: confirmed not used in production.
- `blocked`: known access, compliance, cost, or technical blocker.

## Global Notes

- Public SDK Discover output does not expose category, expanded queries, search lanes, raw candidates, dedupe, reranker inputs, or enrichment routing.
- Local SDK/repo availability does not prove production Discover uses that source.
- Rows should be updated as Shahar/backend answers or setup validation traces arrive.
- For architecture conclusions, `task_source` and `local_sdk` evidence are hypotheses until confirmed by `shahar_confirmed` or `setup_validation_observed`.

## Summary Matrix

| Category | Candidate source/search lane | Candidate enrichment | Main useful fields | Evidence | Confidence | Production status | Notes |
|---|---|---|---|---|---|---|---|
| `b2b_contact_data` | `site:linkedin.com/in/` | LinkedIn person profile scraper/dataset | name, title, company, location, work history, education, skills | task_source, local_sdk | high | unknown | High value, but access/compliance risk. |
| `b2b_contact_data` | `site:linkedin.com/company/` | LinkedIn company scraper/dataset | company name, industry, headcount, location, employees, description | task_source, local_sdk | high | unknown | Needs Shahar confirmation for production availability. |
| `b2b_contact_data` | `site:crunchbase.com/person/` | Crunchbase/person-capable route if available | person, role, organization, profile facts | task_source | medium | unknown | Local Crunchbase company dataset visible; person route needs confirmation. |
| `b2b_contact_data` | `site:crunchbase.com/organization/` | Crunchbase company dataset | company, funding, industry, location, investors, description | task_source, local_sdk | high | unknown | Strong company firmographic candidate. |
| `b2b_contact_data` | enriched company/person datasets | companies enriched / employees enriched datasets | company attributes, employee/profile enrichment | local_sdk, inferred | medium | unknown | Candidate enrichment source, but must confirm fit and compliance. |
| `price_intelligence` | Google Shopping / `udm=28` | Google Shopping dataset/search | product, price, seller, rating, shipping, availability | task_source, local_sdk | high | unknown | Good broad comparison lane. |
| `price_intelligence` | `site:amazon.com/dp/` | Amazon product scraper/dataset | product title, price, rating, reviews, availability, variants | task_source, local_sdk | high | unknown | Strong PDP lane. |
| `price_intelligence` | `site:walmart.com/ip/` | Walmart product scraper/dataset | product title, price, seller, stock, rating, variants | task_source, local_sdk | high | unknown | Strong PDP lane. |
| `price_intelligence` | Best Buy product pages | Best Buy product dataset/scraper | product, price, SKU, rating, availability | task_source, local_sdk | high | unknown | Useful for electronics. |
| `price_intelligence` | eBay product/listing pages | eBay product dataset/scraper | listing title, price, seller, condition, shipping | task_source, local_sdk | high | unknown | Good marketplace lane; may need dedupe/entity normalization. |
| `price_intelligence` | retailer PDPs: Home Depot, Lowes, Costco, Kroger, Ikea, etc. | retailer-specific datasets | product, price, availability, rating, SKU | local_sdk, inferred | medium | unknown | Useful for category expansion after setup validation. |
| `social_media_video` | Google Videos / `tbm=vid` | YouTube/TikTok/Instagram scraper or Web Unlocker fallback | title, URL, creator, thumbnail, duration, snippet | task_source, local_sdk | high | unknown | Discovery lane; enrichment should route platform URLs to WSAPI/scraper. |
| `social_media_video` | Google short-video vertical / `udm=39` | TikTok/YouTube/Instagram scraper | short-video URL, caption, creator, views, likes, comments | task_source | high | unknown | Important Shahar question: does `udm=39` return reliable metadata? |
| `social_media_video` | `site:tiktok.com` | TikTok posts/profile scraper/dataset | caption, creator, hashtags, views, likes, comments, post date | task_source, local_sdk | high | unknown | Markdown likely weak due to JS/anti-bot. |
| `social_media_video` | `site:youtube.com/watch` | YouTube videos scraper/dataset | title, channel, views, likes, comments, transcript/description | task_source, local_sdk | high | unknown | Good long-form and Shorts candidate. |
| `social_media_video` | Instagram Reels / Instagram URLs | Instagram reels/posts scraper/dataset | caption, creator, likes, comments, media metadata | task_source, local_sdk | high | unknown | Access and completeness need validation. |
| `social_media_video` | Facebook reels/video URLs | Facebook reels/posts dataset | creator/page, engagement, caption, media metadata | local_sdk, inferred | medium | unknown | Candidate extension, not in task-source core recommendation. |
| `job_market` | Google Jobs vertical / `ibp=htl;jobs` | Indeed/LinkedIn Jobs/Glassdoor scraper, Web Unlocker for ATS pages | title, company, location, salary, requirements, posted date | task_source, local_sdk | high | unknown | Need confirm whether Google Jobs vertical is available in current SERP path. |
| `job_market` | Indeed job pages | Indeed jobs dataset/scraper | title, company, location, salary, description, posting date | task_source, local_sdk | high | unknown | Strong structured candidate. |
| `job_market` | LinkedIn Jobs | LinkedIn job listings dataset/scraper | title, company, location, description, seniority | task_source, local_sdk | high | unknown | Access/compliance risk. |
| `job_market` | Glassdoor jobs/salaries | Glassdoor jobs/company/reviews datasets | salary, company, title, reviews, location | task_source, local_sdk | high | unknown | Useful for compensation and company signals. |
| `job_market` | Greenhouse / Lever / company career pages | Web Unlocker markdown or custom extraction | job title, company, location, description, requirements | task_source, inferred | medium | unknown | Broad fallback lane; schema extraction may be weaker. |
| `news_media` | Google News / `tbm=nws` | Web Unlocker markdown, news datasets where available | headline, outlet, byline, date, body, topic relevance | task_source, local_sdk | high | unknown | Primary discovery lane. |
| `news_media` | recency filter `tbs=qdr:h` or `tbs=qdr:d` | Web Unlocker markdown | recent headline/body/source/date | task_source | high | unknown | Need confirm SERP support and exact parameterization. |
| `news_media` | BBC URLs | BBC news dataset/scraper | headline, body, date, author, section | task_source, local_sdk | high | unknown | Good supported giant candidate. |
| `news_media` | CNN URLs | CNN news dataset/scraper | headline, body, date, author, section | task_source, local_sdk | high | unknown | Good supported giant candidate. |
| `news_media` | broad news domains | Web Unlocker markdown | headline, body, date, outlet | task_source, inferred | high | unknown | Needed because news spans many domains; paywalls/body extraction risk. |
| `real_estate` | `site:zillow.com/homedetails/` | Zillow properties/price history dataset | address, price, beds, baths, sqft, lot, status, price history | task_source, local_sdk | high | unknown | Strong structured candidate. |
| `real_estate` | Redfin property pages | Web Unlocker or real-estate-specific route if available | address, price, property facts, status | task_source, inferred | medium | unknown | Need confirm supported scraper/dataset. |
| `real_estate` | Realtor property pages | Realtor/international property dataset or Web Unlocker | address, price, beds, baths, sqft, status | task_source, local_sdk | medium | unknown | Local realtor international dataset visible; exact US PDP support needs confirmation. |
| `real_estate` | Airbnb/Booking pages | Airbnb/Booking datasets | listing price, location, amenities, availability | task_source, local_sdk | medium | unknown | More travel/lodging than classic real estate; useful for niche cases. |
| `real_estate` | regional real-estate datasets | Metrocuadrado, Properati, Otodom, Zoopla, etc. | property facts, price, location, status | local_sdk, inferred | medium | unknown | Useful for international/regional variants. |
| `financial_data` | `site:sec.gov/cgi-bin/browse-edgar` | Web Unlocker / PDF extraction | filing type, company, date, filing text, accession | task_source | high | unknown | Need robust SEC/PDF handling. |
| `financial_data` | `filetype:pdf` investor presentations / earnings calls | Web Unlocker / PDF extraction | company, period, transcript/presentation text, metrics | task_source | medium | unknown | Extraction quality can vary. |
| `financial_data` | Yahoo Finance | Yahoo Finance dataset/scraper | ticker, price, company, finance metrics | task_source, local_sdk | high | unknown | Strong structured finance source. |
| `financial_data` | Indeed/Glassdoor alternative data | Indeed/Glassdoor datasets | hiring velocity, employee sentiment, company/job signals | task_source, local_sdk | medium | unknown | Useful as alt-data, not core filings. |
| `financial_data` | official company investor relations pages | Web Unlocker markdown/PDF | press releases, transcripts, reports, presentations | inferred | medium | unknown | Candidate lane for official sources. |

## Category Notes

### `b2b_contact_data`

Goal:
- discover professional profiles, people, company firmographics, and enrichment sources for B2B contact lists.

Most likely strong lanes:
- LinkedIn person profiles,
- LinkedIn company profiles,
- Crunchbase organizations,
- enriched company/employee datasets.

Main risks:
- LinkedIn access and compliance,
- profile/contact data policy,
- confusing person pages, company pages, job pages, and HR content,
- source freshness and completeness.

Questions for Shahar:
- Are LinkedIn and Crunchbase routes available in production Discover?
- Which WSAPI/dataset route is mandatory versus optional?
- Are B2B contact fields allowed and expected?

### `price_intelligence`

Goal:
- discover product pages, prices, stock, discounts, reviews, and seller information.

Most likely strong lanes:
- Google Shopping,
- Amazon PDPs,
- Walmart PDPs,
- Best Buy,
- eBay,
- major retailer PDP datasets.

Main risks:
- duplicate products across sellers,
- stale prices,
- marketplace listing variability,
- coupon/review/blog noise,
- normalizing the same product across retailers.

Questions for Shahar:
- Is Google Shopping available as a search lane?
- Which retailer scrapers/datasets are preferred for production?
- How fresh must prices be for benchmark relevance?

### `social_media_video`

Goal:
- discover video content and enrich engagement/caption/transcript metadata.

Most likely strong lanes:
- Google Videos,
- Google short-video vertical,
- TikTok site search,
- YouTube watch pages,
- Instagram Reels.

Main risks:
- Web Unlocker markdown failure on JS-heavy platforms,
- anti-bot/access issues,
- missing engagement metrics,
- platform-specific schemas,
- stale engagement counts.

Questions for Shahar:
- Does `udm=39` reliably return short-video metadata?
- Should TikTok/YouTube/Instagram URLs always route to WSAPI/platform scrapers?
- Can transcript/caption fields be expected?

### `job_market`

Goal:
- discover active job listings, salary signals, company hiring signals, and skill requirements.

Most likely strong lanes:
- Google Jobs,
- Indeed,
- LinkedIn Jobs,
- Glassdoor,
- Greenhouse/Lever/company career pages.

Main risks:
- stale or expired jobs,
- duplicate listings,
- staffing/marketing/resume-advice noise,
- salary missingness,
- ATS pages with inconsistent HTML.

Questions for Shahar:
- Is Google Jobs available as a SERP vertical?
- Which job sources should be preferred?
- Should expired postings be hard failures?

### `news_media`

Goal:
- discover recent, relevant news articles from credible sources.

Most likely strong lanes:
- Google News,
- recency-filtered news search,
- Web Unlocker for broad news domains,
- specific supported news datasets like BBC and CNN.

Main risks:
- paywalls,
- aggregator pages,
- PR distribution,
- opinion/blog content,
- body extraction failures,
- freshness requirements.

Questions for Shahar:
- What freshness windows matter: past hour, day, week?
- Should PR wires be excluded?
- Which news sources have supported structured routes?

### `real_estate`

Goal:
- discover property listing pages and enrich property facts, pricing, status, and history.

Most likely strong lanes:
- Zillow,
- Realtor,
- Redfin,
- Airbnb/Booking for niche lodging cases,
- regional real-estate datasets.

Main risks:
- stale property status,
- duplicate listings,
- region-specific source coverage,
- missing structured fields,
- markdown pages not enough for price history/comparables.

Questions for Shahar:
- Which real-estate sources are supported in production?
- Is Zillow the main structured route?
- What property fields are required for relevance?

### `financial_data`

Goal:
- discover regulatory filings, earnings material, official investor documents, and alternative financial signals.

Most likely strong lanes:
- SEC filings,
- official PDFs,
- investor relations pages,
- Yahoo Finance,
- Indeed/Glassdoor alternative signals.

Main risks:
- PDF extraction quality,
- wrong filing type,
- unofficial/low-quality financial commentary,
- stale data,
- mixing primary financial sources with social/forum noise.

Questions for Shahar:
- Should SEC/official documents be prioritized over finance media?
- Are PDFs supported robustly through Web Unlocker?
- Which alternative data sources are acceptable?

## Update Rules

When Shahar/backend answers arrive:

- Change `production status` from `unknown` to `confirmed`, `not_used`, or `blocked`.
- Add `shahar_confirmed` to the evidence column.
- Correct the candidate enrichment route if production routing differs.
- Add trace-specific notes if a sample run confirms or disproves assumptions.

When setup validation traces arrive:

- Add `setup_validation_observed` to evidence.
- Split rows if one source has multiple enrichment paths.
- Mark failure modes observed during setup validation.
- Update confidence based on actual relevance, enrichment success, and HFTE usefulness.

## Immediate Gaps

- Need Shahar confirmation of production routing.
- Need Tavily and Exa fair-run settings before competitor comparison.
- Need setup validation category selection before deep Category Output Contract.
- Need actual traces or proxy outputs before architecture failure attribution.
