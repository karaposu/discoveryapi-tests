# discoveryapi query-expansion experiments

This project is related to `discoveryapi` inner workings and currently focuses on query expansions. The main subfocus is the B2B vertical, due to limited resources and time.

I designated 9 different paradigms by which a query can be manipulated for expansion.


## Expansion paradigms

1. **intent_and_terminology**
   - **def:** Change role, industry, or concept wording while preserving the user's intent.
   - **example:**
     - "Head of Sales" → "VP Sales"
     - "cybersecurity SaaS" → "security software"
2. **entity_targeting**
   - **def:** Choose what kind of result the expansion is trying to find: person profiles, company profiles, or a mix.
   - **example:**
     - `site:linkedin.com/in "VP Sales" "cybersecurity SaaS"`
     - `site:linkedin.com/company "cybersecurity SaaS startup"`
3. **discovery_flow**
   - **def:** Choose the discovery path: person-first, company-first, or mixed.
   - **example:**
     - `"VP Sales" "cybersecurity SaaS"`
     - `"cybersecurity SaaS startup" site:crunchbase.com/organization`
4. **source_lane_targeting**
   - **def:** Aim at a specific source family or shape (LinkedIn, Crunchbase, company team pages, general web).
   - **example:**
     - `site:linkedin.com/in "VP Sales" "cybersecurity SaaS"`
     - `site:crunchbase.com/organization "cybersecurity SaaS"`
5. **constraint_handling**
   - **def:** Decide which original constraints to preserve and which to broaden.
   - **example:**
     - Preserve geography, broaden title: `("VP Sales" OR "Head of Sales" OR "Sales Director") "cybersecurity SaaS" "United States"`
     - Broaden industry, keep title: `"VP Sales" ("cybersecurity SaaS" OR "security software" OR "SaaS startup")`
6. **field_and_evidence_targeting**
   - **def:** Bias the expansion toward sources likely to expose specific B2B contract fields.
   - **example:**
     - `"VP Sales" "cybersecurity SaaS" "currently" site:linkedin.com/in`
     - `"cybersecurity SaaS" ("headquartered" OR "headcount" OR "funding") site:crunchbase.com`
7. **noise_control**
   - **def:** Actively avoid known bad result types.
   - **example:**
     - Exclude job/career noise: `"VP Sales" "cybersecurity SaaS" -jobs -hiring -resume`
     - Exclude HR-software and recruiting blogs: `"VP Sales" "cybersecurity SaaS" -"hr software" -"recruiting tips"`
8. **query_syntax_shaping**
   - **def:** Control how the query is expressed (quoted phrases, `site:` operators, boolean `OR`, negative `-keyword` exclusions).
   - **example:**
     - Quoted phrase + site operator: `site:linkedin.com/in "VP Sales" "cybersecurity SaaS"`
     - Boolean OR + negative term: `("VP Sales" OR "Head of Sales") "cybersecurity SaaS" -jobs`
9. **tool_and_evidence_mode_targeting**
   - **def:** Shape the expansion for the downstream evidence channel (SERP URL discovery, structured enrichment, dataset lookup).
   - **example:**
     - `bright_data.google_serp(query="\"VP Sales\" \"cybersecurity SaaS\"", top_n=10)`
     - `wsapi.linkedin.person_lookup(name="Jane Doe", company="CyberX SaaS")`


## Evaluation

Once a query is expanded and used for SERP, I gather the links, metadata, and snippets, and for each link I ask the judge LLM 10 predefined boolean questions tailored to the B2B vertical. The sum of `True` answers is the `total_point` score and approximates how good the expansion was — a good expansion should produce better SERP results.

More on the boolean-vs-numeric scoring rationale: [Stop asking LLMs for numbers — why boolean classification beats confidence scores](https://medium.com/@enesesvetkuzucu/stop-asking-llms-for-numbers-why-boolean-classification-beats-confidence-scores-fb67438826e5).

### Judge questions

Source of truth: `src/expansion/llm_based/judge_logic.py::QUESTIONS`.

1. **is_b2b_contact_data_candidate** — Is this result a B2B contact-data candidate, not merely a generic article, product page, blog post, or topical page?
2. **matches_requested_entity_type** — Does the result match the entity type requested or implied by the query (person, company, or mixed person-company)?
3. **satisfies_explicit_query_constraints** — Does the result satisfy the query's explicit constraints — role/title, industry, geography, seniority, company type, or company stage?
4. **exposes_core_identity_fields** — Does the result expose the core identity fields required for its result type? For a person/mixed result: person name + current title or current company + profile URL. For a company/mixed result: company name + domain/profile URL or business description.
5. **exposes_useful_extra_b2b_field** — Does the result expose at least one useful extra B2B field for its result type? Person examples: location, seniority, department/function, work history, tenure, education, skills, professional summary. Company examples: headquarters, headcount, funding, investors, employee count, founded year, growth signal.
6. **credited_fields_visible_in_evidence** — Are the fields you would credit visibly supported by the returned evidence (link/title/snippet), not inferred from outside knowledge?
7. **suitable_professional_or_company_source** — Is the source or page type suitable for professional or company data (professional profile, company page, firmographic record, team page, or credible public web page)?
8. **shows_current_professional_or_company_context** — Does the result show current professional or company context, not only historical, stale, or ambiguous references?
9. **free_of_known_noise_page_types** — Is the result free of known noise page types (job postings, career advice, resume templates, HR/recruiting software pages, staffing-agency marketing pages, generic HR blogs, unsupported lead directories)?
10. **free_of_visible_wrong_match_failures** — Is the result free of visible wrong-match failures (wrong industry, geography, seniority, company stage, company, person, or entity type)?

Each candidate gets a `total_point` score: the count of `True` answers, range `0..10`. Higher = stronger B2B contact-data evidence.


## How to run

The pipeline is two steps. SERP (paid Bright Data quota) is decoupled from judging (paid OpenAI tokens), so the judge can be re-run any number of times against a single SERP fetch — try a different judge model, tweak the prompt, etc., without burning more SERP quota.

**Prerequisite**: a `.env` file with `OPENAI_API_KEY` and `BRIGHTDATA_API_TOKEN`.

### Step 1 — generate variants and fetch SERP results

```bash
python src/expansion/llm_based/b2b_vertical_expansion_and_serp.py
```

What it does:

- **Phase A**: one LLM call asks for `VARIANTS_PER_SEED` (default: 3) query variants per paradigm seed. The `verbatim` baseline is added in Python — no LLM call needed for it.
- **Phase B**: for each variant, run a Google SERP query through Bright Data and keep the top `SERP_RESULTS_PER_VARIANT` (default: 5) results.

Output:

```
outputs/b2b_vertical_expansion_and_serp_<YYYYMMDD_HHMMSS>.json
```

The report contains the query spec, every variant (with its seeds + rationale + query), and the SERP results for each variant. `serp_results[i].llm_judge_result` is `null` here — judging happens in step 2.

To change the query, the paradigm seeds, `VARIANTS_PER_SEED`, or the SERP defaults (location / language / device / N), edit the top of `b2b_vertical_expansion_and_serp.py`, `variant_generation.py`, or `serp.py`. There are no CLI flags.

### Step 2 — score every SERP candidate with the LLM judge

```bash
python src/expansion/llm_based/add_score.py outputs/b2b_vertical_expansion_and_serp_<YYYYMMDD_HHMMSS>.json
```

What it does: reads the step-1 report, calls the LLM judge (the 10 boolean questions above) once per SERP candidate, and writes a new report next to the input:

```
outputs/b2b_vertical_expansion_and_serp_<YYYYMMDD_HHMMSS>_scored.json
```

The scored report adds:

- `serp_results[i].llm_judge_result` — the 10 booleans + `total_point` (sum of True) per candidate
- `variants[i].scoring` — per-variant aggregate (`mean_total_point`, `sum_total_point`, `max_total_point`, `min_total_point`, per-candidate scores)
- `judging` block at the top — run-level aggregate + a `variant_ranking` sorted by mean score

Optional: `--output <path>` to write the scored report to a custom location.
