[27.04.2026, 12:15:35] Shahar Brightdata: So for each category, I need you to test the architecture and see if it is better than current discover API, and if there is anything that better to change (intent, search engine, use WSAPIs, datasets or anything else)
Once you done with one category - create a report and sent me, than move to the second (in other words - dont wait for me).
If there anything you need from me (more info on models, api keys, etc) LMK and I will take care of it.
We need the report to show results of at least 50 queries per category (if you think more, than more) and compare: Tavily, Exa, current Discover API, and new arcithechuer versions.
[27.04.2026, 12:16:02] Shahar Brightdata: North Star KPIs:
These metrics serve as the single source of truth for Product, Engineering, and Marketing alignment.
1.⁠ ⁠High-Fidelity Token Efficiency (HFTE)
Definition: The ratio of Relevant Signal (unstable facts/data) to Total Tokens returned per query.
The Goal: Maximize information density. The system must strip non-essential HTML elements (ads, navigation, scripts) to ensure the customer pays only for content, not noise.
Strategic Value: In the agent economy, context window usage equals cost. Optimizing token efficiency is a critical competitive differentiator against wrapper APIs.
1.⁠ ⁠Reranking Effectiveness (nDCG@5)
Definition: The quality score of the Top-5 results when benchmarked against a "Golden Dataset" of complex agentic queries.
The Goal: Achieve a >20% quality lift over raw SERP (Google/Bing) rankings.
Strategic Value: Standard search engines rank for SEO and ad revenue. We must rank for Agent Intent. If the most relevant answer is technically located at result #8, our Reranker must elevate it to #1 to ensure accurate retrieval.
1.⁠ ⁠High-Concurrency Throughput
Definition: The success rate of search requests that spawn >10 concurrent sub-fetches (deep dives) and return full context in <1.5 seconds.
The Goal: Eliminate latency penalties for deep research tasks.
Strategic Value: This metric validates our "Unfair Advantage." While competitors throttle concurrency due to upstream limitations, our owned infrastructure allows for massive parallel processing, defining our position in the market.
[27.04.2026, 12:17:10] Shahar Brightdata: Last point is the least important, but we do want to track it





i asked what he measn


I meant that Discover API is currently built from its taking category and using Google Gemini. It's built for subcategories, and for each, it's taking the first 20 results from Google. And this is how it's built, 80 results, and then do again by intent. There is a plate to do with this,  on the serp, you have, you know, a few options, and then you can go to Explore APIs, and you can go to datasets, et cetera, et cetera. So for that, I'm not talking about the ranking, more about not say about the queries, but more about what we call search engine. It could be Google, it could be the general Google, which is what we're using right now. It could be like videos or short videos or images or any other things under Google, and it could be different search engines, but there is a problem with those that are pretty slow, but if it's well fit, so this is good. And for company data, for instance, it could be LinkedIn or Indeed, something like this. Videos, it might be YouTube, et cetera, but there is also the problem that we need to return the same data. So when we look on different search engines, we just need to be sure that if we want one for LinkedIn and one for Indeed and one for Google, there is valuable data that we can get on all of them and return from all of them.