# Task 1 Runner — Step-by-Step Work Logic

This document explains, one step at a time, what happens when you run the experiment. Every step references the code that actually performs the work, so you can follow along in the source.

The system is split across three files:

| File | Role |
|---|---|
| `runner.py` | Thin entry point. Loads env, calls into `experiment`, writes the report path. |
| `config.py` | All knobs: query, models, counts, locale, and the `EXPANSION_COMBINATIONS` list. Also bootstraps `sys.path`. |
| `experiment.py` | The pipeline: build LLM contract, ask OpenAI to render each combination, run SERP, judge top-N candidates, build the report. |

The runner has **no CLI flags**. To change a value, edit `config.py` and re-run.

Entry point: `runner.py:58` (`if __name__ == "__main__"`) → `main()` at `runner.py:15`.

---

## Step 0 — Process start

You run:

```bash
.venv/bin/python runner.py
```

Python imports `runner.py`. Its first non-stdlib import is `from config import PROJECT_ROOT` (`runner.py:11`). Importing `config` triggers the `sys.path` bootstrap at `config.py:15-21`:

- `PROJECT_ROOT` = the repo directory itself, so `expansion_schemas`, `llm_request_logic`, `retrieval`, and `evaluation` resolve as top-level modules.
- `SDK_SRC` = `/Users/ns/Desktop/projects/sdk-python/src`, the local Bright Data SDK source. This is **prepended** to `sys.path`, so `import brightdata` resolves to the local SDK rather than the installed `brightdata-sdk` package.

Then `runner.py:12` imports `run, save_report` from `experiment.py`, and `experiment.py` re-imports `config` (already cached) plus the schema modules. The order works because `config` patches `sys.path` first.

`if __name__ == "__main__"` triggers `main()`.

---

## Step 1 — Load environment variables

`main()` (`runner.py:15`) first calls `load_project_env()` (`runner.py:23`).

- Looks for `./.env`.
- Prefers `python-dotenv` if installed; otherwise parses the file manually.
- Populates `os.environ` with `BRIGHTDATA_API_TOKEN`, `BRIGHTDATA_WEBUNLOCKER_BEARER`, `OPENAI_API_KEY`, etc.
- It does **not** override variables that are already set in the shell.

After this step, both OpenAI and Bright Data have the credentials they need.

---

## Step 2 — Configuration (constants in `config.py`)

There is no `parse_args()` call. All knobs are module-level constants in `config.py`:

### 2a. Run-shape and locale (`config.py:42-89`)

| Constant | Value | Purpose |
|---|---|---|
| `QUERY` (`config.py:52`) | `B2B_QUERY_EXAMPLES[0]` | The original user query being expanded |
| `PROMPT_VERSION` (`config.py:57`) | `"b2b_contact_data_default_v1"` | Label stamped on the report |
| `LLM_MODEL` (`config.py:59`) | `"gpt-4o"` | Model used to render each combination |
| `JUDGE_MODEL` (`config.py:60`) | `"gpt-4o"` | Model used to answer the 10 boolean judge questions |
| `RESULT_COUNT` (`config.py:62`) | `10` | How many SERP results to ask Bright Data for, per combination |
| `JUDGE_TOP_N` (`config.py:63`) | `5` | How many of those SERP results to actually judge |
| `SKIP_JUDGE` (`config.py:64`) | `False` | If `True`, run expansion + SERP only, no LLM judging |
| `LOCATION` / `LANGUAGE` / `DEVICE` (`config.py:69-71`) | `"United States"` / `"en"` / `"desktop"` | Bright Data SERP locale/device |
| `BRIGHTDATA_TOKEN` (`config.py:76`) | `None` | If `None`, the SDK uses `BRIGHTDATA_API_TOKEN` from env |
| `SERP_ZONE` (`config.py:77`) | `None` | If `None`, the SDK uses its configured zone |
| `AUTO_CREATE_ZONES` (`config.py:78`) | `True` | Whether the SDK may auto-create missing zones |
| `DEFAULT_TARGET_FIELDS` (`config.py:94`) | 21 fields | Person + company creditable fields from the category contract |
| `DEFAULT_EXCLUSIONS` (`config.py:119`) | 8 tags | Known B2B noise tags |

There is no `NUM_EXPANSIONS` — the number of expansions is now `len(EXPANSION_COMBINATIONS)`.

### 2b. Expansion combinations (`config.py:160`)

This is the key change vs. earlier versions. `EXPANSION_COMBINATIONS` is a list of `ExpansionCombination` objects (`expansion_paradigm_types.py:255`). Each combination is a **fully-specified paradigm + parameters bundle** — paradigms, source lane, syntax strategy, exclusion strength, target fields, industry/geography constraints, etc. are all fixed in code, **not chosen by the LLM**.

Currently 5 combinations are seeded:

| label | source_lane | syntax_strategy | exclusion_strength | recipe_name |
|---|---|---|---|---|
| `linkedin_person_strict` | linkedin_person | site_operator | strict | Source-Aware Person-First |
| `linkedin_person_boolean_or` | linkedin_person | boolean_or | moderate | Broad Semantic Recall |
| `linkedin_company` | linkedin_company | site_operator | moderate | Source-Aware Company-First |
| `crunchbase_company` | crunchbase_company | site_operator | light | Field-Intent Enriched-Data |
| `general_web_exclusion_heavy` | general_web | negative_terms | strict | Exclusion-Heavy Precision |

Each combination's `parameters` field is an `ExpansionParameters` instance (`expansion_paradigm_types.py:234`) — the type that was always defined but never used before this refactor.

`main()` then calls `run()` (`experiment.py:64`) via the re-export at `runner.py:12`.

---

## Step 3 — Stamp the run

`run()` (`experiment.py:64`) first records:

- `started_at` = current UTC time.
- `run_id` = `b2b_YYYYMMDD_HHMMSS` (UTC).

These are written into the report skeleton so every output file is traceable to a specific moment.

---

## Step 4 — Build the experiment config (report metadata)

`build_expansion_config()` (`experiment.py:123`) produces an `ExpansionExperimentConfig` (`expansion_schemas.py:134`). In the new flow this is **only metadata for the report** — it is not sent to the LLM. It still records:

- `model` = `LLM_MODEL`, `prompt_version` = `PROMPT_VERSION`.
- `num_expansions` = `len(EXPANSION_COMBINATIONS)` (derived, not a separate knob).
- `allowed_entity_types`, `allowed_source_lanes`, `allowed_evidence_modes` — full enumerations of the relevant `expansion_schemas` enums.
- `allowed_target_fields` = `DEFAULT_TARGET_FIELDS`.
- `allowed_exclusions` = `DEFAULT_EXCLUSIONS`.
- `fixed_retrieval_method` = `"bright_data_google_serp"`.
- `fixed_result_count` = `RESULT_COUNT`.
- `locale` = `LOCATION`.

This config plus the `combinations` field in the report tells a reader exactly what shape the run had.

---

## Step 5 — Loop over combinations and call the LLM (one call per combination)

This is the heart of the new flow. `run()` (`experiment.py:80-100`) iterates `EXPANSION_COMBINATIONS` and, for each one, makes a single LLM call:

```python
for index, combination in enumerate(EXPANSION_COMBINATIONS, start=1):
    draft = request_expansion_for_combination(
        original_query=QUERY,
        combination=combination,
        model=LLM_MODEL,
    )
    expansion_items.append(
        build_expansion_output_item(combination, draft, index)
    )
```

### 5a. Render one combination — `request_expansion_for_combination()` (`llm_request_logic.py:234`)

For each combination:

1. `create_openai_chat_model(model=LLM_MODEL)` instantiates `ChatOpenAI` at `temperature=0.0` (`llm_request_logic.py:70`).
2. `llm.with_structured_output(CombinationExpansionDraft, method="function_calling")` enforces the response schema (`expansion_schemas.py:212`). `method="function_calling"` is used here (and everywhere else `with_structured_output` is called) to avoid OpenAI's new strict-mode response_format rejecting our schemas because of `Optional` fields and `Dict[str, str]` defaults.
3. `build_combination_prompt()` (`llm_request_logic.py:223`) assembles a two-message `ChatPromptTemplate`:
   - **System** = `COMBINATION_SYSTEM_PROMPT` (`llm_request_logic.py:159`). This is the critical change vs. the old free-form flow — it gives the LLM **explicit operator-encoding rules**:
     - `source_lane` → which `site:` operator (e.g., `linkedin_person → site:linkedin.com/in`).
     - `syntax_strategy` → the dominant mechanic (`site_operator` requires `site:`, `boolean_or` requires `("A" OR "B")`, `negative_terms` requires `-prefix`, etc.).
     - `exclusion_strength` → how many negative tokens (`strict` = 5+, `moderate` = 3-4, `light` = 1-2).
     - Concrete mappings from abstract exclusion tags (`job_postings → -jobs -hiring -"job posting" -careers`).
     - "Do not pick enum values. Do not produce more than one query."
   - **User** = `COMBINATION_USER_PROMPT` (`llm_request_logic.py:211`) interpolated with the original query and the JSON dump of the combination.
4. `chain.invoke(...)` sends both messages to OpenAI.
5. OpenAI returns a `CombinationExpansionDraft` (`expansion_schemas.py:212`) — deliberately small:

```python
class CombinationExpansionDraft(BaseModel):
    query: str                                                # the concrete Google query
    preserved_constraints: List[ExpansionOutputConstraintValue]
    broadened_constraints: List[ExpansionOutputConstraintValue]
    broadening_axis: ExpansionOutputBroadeningAxis
    rationale: str
    risk_notes: List[str]
```

Because the LLM only fills in `query` and the trace narrative — **not** entity_type, source_lane, paradigms, target_fields, exclusions, etc. — it can't hallucinate enum values for those fields. The combination already supplies them.

### 5b. Wrap draft + combination into `ExpansionOutputItem` — `build_expansion_output_item()` (`experiment.py:154`)

The LLM-returned draft is small; we still want full `ExpansionOutputItem` records (`expansion_schemas.py:177`) in the report for compatibility with the existing judging loop. `build_expansion_output_item()` does that translation purely in Python:

- `expansion_id` = `f"exp_{index:02d}_{combination.label}"` — easy to grep, like `exp_01_linkedin_person_strict`.
- `entity_type`, `source_lane`, `expected_evidence_mode`, `discovery_flow`, `syntax_strategy` — taken from `combination.parameters` and converted from `expansion_paradigm_types` enums into their `expansion_schemas` counterparts by `.value`.
- `target_fields`, `exclusions` — taken from `combination.parameters`.
- `query`, `preserved_constraints`, `broadened_constraints`, `broadening_axis`, `rationale`, `risk_notes` — taken from the LLM draft.
- `expansion_trace.recipe_name` and `expansion_trace.paradigms` — taken from the combination, **not** from the LLM. No more hallucinated recipe names.
- `metadata = {"combination_label": combination.label}` — lets the report join back to the combination definition.

### 5c. Wrap all items in `ExpansionOutputResult`

After the loop, `run()` assembles a single `ExpansionOutputResult` (`expansion_schemas.py:196`) wrapping every `ExpansionOutputItem`. This keeps the downstream report shape compatible with the previous version of the runner — the judging loop just iterates `expansion_result.expansions`.

---

## Step 6 — Initialize the Bright Data SERP client

`run()` then constructs `BrightDataGoogleSERPRetrievalClient` (`retrieval/bright_data_serp.py:32`, called at `experiment.py:102-109`):

- `token` = `BRIGHTDATA_TOKEN` (defaults to `None`; the SDK falls back to `BRIGHTDATA_API_TOKEN` from env).
- `serp_zone` = `SERP_ZONE` (defaults to `None`, letting the SDK use its configured zone).
- `auto_create_zones` = `AUTO_CREATE_ZONES` (defaults to `True`).
- `default_location`, `default_language`, `default_device` = `LOCATION`, `LANGUAGE`, `DEVICE`.

The client wraps `BrightDataClient.search.google(...)` from the local SDK at `/Users/ns/Desktop/projects/sdk-python/src/brightdata/`.

---

## Step 7 — Retrieval + judging loop

`run_retrieval_and_judging()` (`experiment.py:199`) iterates the `ExpansionOutputItem`s from Step 5. For each one:

### 7a. Run Google SERP

`retrieval_client.search_sync(query=expansion.query, …)` (`retrieval/bright_data_serp.py:88`) wraps the async `search()` in `asyncio.run`. Inside `search()` (`retrieval/bright_data_serp.py:53`):

1. Opens an `async with BrightDataClient(...)` session.
2. Calls `client.search.google(query=..., zone=..., location=..., language=..., device=..., num_results=RESULT_COUNT)`.
3. The SDK returns a single `SearchResult`. The client passes it to `normalize_google_serp_result()` (`retrieval/bright_data_serp.py:113`).
4. Normalization converts each SERP item into a `RetrievedCandidate` (`retrieval/schemas.py:10`) with `rank`, `source_name="bright_data_google_serp"`, `url`, `title`, `snippet`, `structured_fields` (displayed_url, country, totals), and `raw` (the original SDK item).

This produces up to `RESULT_COUNT` candidates per expansion. Crucially, the `query` string here is the **operator-encoded** form from Step 5a (e.g., `site:linkedin.com/in ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" "United States" -jobs -hiring ...`) — that's the whole point of the combination flow.

### 7b. Slice to top-N for judging

`candidates[:JUDGE_TOP_N]` (`experiment.py:222`). By default, the top 5 of the 10 SERP candidates are sent to the judge.

### 7c. Judge each candidate (skipped if `SKIP_JUDGE = True`)

For each of those top-N candidates, `request_b2b_boolean_judge_output()` (`evaluation/b2b/boolean_questions.py:254`) is called.

Inside it:

1. `create_openai_boolean_judge_chat_model(model=JUDGE_MODEL)` instantiates a fresh `ChatOpenAI` at `temperature=0.0` (`evaluation/b2b/boolean_questions.py:221`).
2. `llm.with_structured_output(B2BBooleanJudgeOutputResult, method="function_calling")` enforces the answer schema (`evaluation/b2b/boolean_questions.py:58`).
3. `build_b2b_boolean_judge_prompt()` (`evaluation/b2b/boolean_questions.py:243`) assembles:
   - **System** = `B2B_BOOLEAN_JUDGE_SYSTEM_PROMPT` (`evaluation/b2b/boolean_questions.py:153`): boolean only, YES/NO, no scores, no inference beyond visible evidence, no private contact details required, one answer per question id, no extra fields.
   - **User** = `B2B_BOOLEAN_JUDGE_USER_PROMPT` (`evaluation/b2b/boolean_questions.py:169`) interpolated with `original_query`, `candidate_result`, `returned_evidence`, and the 10 questions rendered by `format_boolean_questions()` (`evaluation/b2b/boolean_questions.py:197`).
4. The candidate is passed in via two helper payloads:
   - `candidate_prompt_payload()` (`experiment.py:252`): `rank`, `source_name`, `url`, `title`, `snippet`.
   - `candidate_evidence_payload()` (`experiment.py:262`): `url`, `title`, `snippet`, `content`, `structured_fields`.
5. OpenAI returns a `B2BBooleanJudgeOutputResult` (`evaluation/b2b/boolean_questions.py:58`) — a list of `B2BBooleanJudgeOutputAnswer` (`evaluation/b2b/boolean_questions.py:51`) entries.
6. `_validate_boolean_judge_output_result()` and `_ensure_complete_answer_set()` (`evaluation/b2b/boolean_questions.py:304`) verify exactly one answer per question id — no missing, duplicate, or extra ids — or raise `ValueError`.

The 10 question ids judged for every candidate (`evaluation/b2b/boolean_questions.py:64`):

1. `is_b2b_contact_data_candidate` — Is it a B2B contact-data candidate, not a generic article or product page?
2. `matches_requested_entity_type` — Person / company / mixed match the query?
3. `satisfies_explicit_query_constraints` — Role, industry, geography, seniority, etc. all match?
4. `exposes_core_identity_fields` — Name + title/company + URL for person; name + domain/description for company?
5. `exposes_useful_extra_b2b_field` — At least one bonus field (seniority, work history, funding, headcount, …)?
6. `credited_fields_visible_in_evidence` — Are credited fields actually shown in evidence, not inferred?
7. `suitable_professional_or_company_source` — Is the page type appropriate?
8. `shows_current_professional_or_company_context` — Current, not stale?
9. `free_of_known_noise_page_types` — No job posts, HR software, career advice, etc.?
10. `free_of_visible_wrong_match_failures` — No wrong industry/geography/seniority/entity-type?

### 7d. Record the per-candidate result

For every candidate (judged or just retrieved), `run_retrieval_and_judging()` appends a record (`experiment.py:233-248`) with:

- `prompt_version`
- `original_query`
- `expansion` — serialized `ExpansionOutputItem`, including `expansion_trace.recipe_name`, `paradigms`, and `metadata.combination_label`. This is what lets you slice the report by combination.
- `retrieved_candidate` — serialized `RetrievedCandidate`.
- `judge_result` — full structured judge output, or `None` if `SKIP_JUDGE = True`.
- `boolean_summary` — built by `summarize_boolean_answers()` (`experiment.py:272`): `yes_count`, `no_count`, `yes_question_ids`, `no_question_ids`.

After all combinations × all top-N candidates have been processed, the loop returns the list of records and `run()` writes them into `report["records"]`.

---

## Step 8 — Finalize the report

`run()` stamps `report["completed_at"]` (`experiment.py:119`) and returns the dict. The final report shape:

```text
{
  run_id,
  started_at,
  query,
  retrieval_method: "bright_data_google_serp",
  skip_judge,
  experiment_config:  ExpansionExperimentConfig (JSON)
  combinations:       List[ExpansionCombination] (JSON — the pre-built bundles)
  expansion_result:   ExpansionOutputResult (JSON — items rendered by the LLM)
  records: [
    {
      prompt_version,
      original_query,
      expansion:          ExpansionOutputItem (with expansion_trace + metadata.combination_label)
      retrieved_candidate: RetrievedCandidate
      judge_result:        B2BBooleanJudgeOutputResult (or null)
      boolean_summary:     { yes_count, no_count, yes_question_ids, no_question_ids }
    },
    ...
  ],
  completed_at
}
```

The `combinations` key is new vs. the previous version — it records the input combinations as-defined in `config.py`, so the report is self-describing without re-reading the source.

---

## Step 9 — Write the report to disk

Back in `main()` (`runner.py:15-21`):

- `save_report()` (`experiment.py:288`) writes JSON (`indent=2`, `default=str` for any non-JSON value) to `outputs/<run_id>.json` (under `DEFAULT_OUTPUT_DIR`, `config.py:89`).
- The parent directory is created if missing.
- The path is printed to stdout and `main()` returns 0.

---

## Summary of API calls per run (with defaults)

| Stage | Call | Count |
|---|---|---|
| Expansion | OpenAI `gpt-4o` via LangChain | **`len(EXPANSION_COMBINATIONS)`** = 5 |
| SERP | Bright Data Google SERP | **`len(EXPANSION_COMBINATIONS)`** = 5 |
| Judging | OpenAI `gpt-4o` via LangChain | **`len(EXPANSION_COMBINATIONS)` × `JUDGE_TOP_N`** = 5 × 5 = 25 |

So a default run = **5 + 5 + 25 = 35 external requests**. This is higher than the previous free-form flow (1 + 5 + 25 = 31) because each combination is now its own LLM call. The tradeoff is clean per-combination attribution: every SERP / judge record can be rolled up by `metadata.combination_label`.

---

## Where the contract pieces fit

- **`b2b_contact_data_category_output_contract.py`** defines *what counts as a good B2B result* (relevance grades, person/company fields, failure tags, coverage math). The runner uses its field lists indirectly via `DEFAULT_TARGET_FIELDS` and `DEFAULT_EXCLUSIONS`.
- **`expansion_paradigm_types.py`** defines *how an expansion can transform a query* — 9 paradigms, parameter enums (source lane, syntax strategy, exclusion strength, …), the `ExpansionParameters` model (`:234`), the `ExpansionCombination` wrapper (`:255`), and the 8 named recipes in `B2B_CONTACT_DATA_EXPANSION_RECIPES` (`:312`). Before the combinations refactor this whole file was defined but never imported; now `ExpansionCombination` and `ExpansionParameters` are the central type for the runtime flow.
- **`expansion_schemas.py`** is the *LLM-boundary contract*:
  - Old flow: `ExpansionInputData` → LLM → `ExpansionOutputResult` (the LLM generated N items, picking paradigms freely).
  - New flow: `ExpansionCombination` → LLM → `CombinationExpansionDraft` (`:212`) → Python wraps each draft + combination into an `ExpansionOutputItem` (`:177`) → all items wrapped in one `ExpansionOutputResult` (`:196`).
- **`llm_request_logic.py`** holds the prompts and request functions. The **active** flow is `request_expansion_for_combination()` (`:234`) plus `COMBINATION_SYSTEM_PROMPT` (`:159`), which encode the operator rules. The **legacy** free-form `request_expansion_output()` (`:104`) and `EXPANSION_SYSTEM_PROMPT` (`:40`) are still present for A/B comparison but `experiment.run()` no longer calls them.
- **`evaluation/b2b/boolean_questions.py`** is the *judging contract*: a fixed 10-question yes/no rubric, so the score logic can be designed later without rerunning the LLM.
- **`retrieval/`** is the *retrieval contract*: provider-neutral `RetrievedCandidate` so SERP today and WSAPI/datasets later can plug into the same judging path.

The point of this separation: every combination is tested against the same retrieval method, locale, and 10-question rubric. Only the combination itself changes, so when the judge YES/NO counts differ between two combinations, the difference is attributable to that one input.
