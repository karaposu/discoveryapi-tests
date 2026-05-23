"""Minimal runnable example of request_query_variants + per-variant SERP.

For each LLM-produced variant, run Bright Data Google SERP and print the
top 5 result URLs.

Uses the shared `schemas.py` types (`ExpansionVariant`,
`ExpansionSerpResult`). Judge logic is NOT included yet — every
`ExpansionSerpResult.llm_judge_result` is left as `None`.

Run:
    python src/expansion/llm_based/minimal3.py

Requires .env with OPENAI_API_KEY and BRIGHTDATA_API_TOKEN.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---- sys.path bootstrap (same shape as experiment.py / config.py) ----

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SDK_SRC = Path("/Users/ns/Desktop/projects/sdk-python/src")

for _path in (PROJECT_ROOT, SDK_SRC):
    p = str(_path)
    if p not in sys.path:
        sys.path.insert(0, p)


from dotenv import load_dotenv  # noqa: E402
from langchain_core.language_models.chat_models import BaseChatModel  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from retrieval import BrightDataGoogleSERPRetrievalClient, RetrievedCandidate  # noqa: E402

from llm_call import call_structured  # noqa: E402
from schemas import ExpansionSerpResult, ExpansionVariant  # noqa: E402


load_dotenv()


DEFAULT_MODEL = "gpt-4o"
SERP_LOCATION = "United States"
SERP_LANGUAGE = "en"
SERP_DEVICE = "desktop"
SERP_RESULTS_PER_VARIANT = 5
OUTPUT_DIR = PROJECT_ROOT / "outputs"


# ---- Logging ----
#
# DEBUG controls verbose per-call logging (LLM call, SERP call sites, etc).
# Toggle this constant to silence/restore. Warnings (e.g. zero SERP
# candidates) print regardless of DEBUG.

DEBUG = True


def _log_debug(message: str) -> None:
    if DEBUG:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        print(f"  [debug {ts}] {message}", flush=True)


def _log_warn(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"  [WARN  {ts}] {message}", flush=True)


# ---- Pydantic schemas ----
#
# Note: The full ExpansionVariant has a `serp_results` field that the LLM
# should NOT populate (Phase B fills it from SERP). To keep the LLM's
# response schema small and prevent it from inventing fake SERP results,
# the LLM returns the slim `_LLMVariantOutput` shape; the runner promotes
# each one to a full `ExpansionVariant` after the SERP step.

class _LLMVariantOutput(BaseModel):
    """The LLM-produced subset of an ExpansionVariant — no serp_results."""
    seeds: List[str] = Field(..., description="Which seed paradigms shaped this variant.")
    query: str = Field(..., description="Google query body, no site: prefix, no -keyword exclusions.")
    rationale: str = Field(..., description="One-sentence explanation.")


class _QueryVariantsResponse(BaseModel):
    variants: List[_LLMVariantOutput]


class B2BQuerySpec(BaseModel):
    natural_query: str
    entity_type: str
    industry: Optional[str] = None
    geography: Optional[str] = None
    company_type: Optional[str] = None
    role_title_family: Optional[str] = None
    seniority_band: Optional[str] = None
    department_or_function: Optional[str] = None


# ---- Prompts ----

_SYSTEM_PROMPT = """You generate semantic query variants for downstream search.

Given a query spec (JSON) and a list of paradigm seeds, produce variants
according to this rule:

  FOR EACH seed in the supplied list, produce EXACTLY {variants_per_seed}
  variants whose primary `seeds` is that seed.

Within a seed's set of variants, each one must explore a DIFFERENT
broadening approach (e.g. for `title_broadening`: one variant broadens to
abbreviations, another to functional synonyms, another to C-suite forms;
for `geography_broadening`: one uses USA/US abbreviations, another uses
regional terms, another adds state-level alternatives). Do not duplicate
a variant within a seed.

Each variant must:
- Preserve the spec's constraints (industry, geography, seniority, role/title family).
- Be shaped by the assigned seed paradigm (and may combine with others
  for the `combined_broadening` seed).
- Use Google syntax for broadenings: ("A" OR "B" OR "C") with parentheses.
- Quote multi-word phrases.
- NOT include site: operators.
- NOT include negative -keyword exclusions.
- NOT use the literal word "AND" between phrases. Google's default
  operator is already implicit AND; uppercase "AND" can be parsed
  literally and return zero results. Just separate phrases with spaces.
    RIGHT: ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" "United States"
    WRONG: ("VP Sales" OR "Head of Sales") AND "cybersecurity SaaS" AND "United States"
- List the seeds it embodies in `seeds`.
- Include a one-sentence rationale that names the specific broadening approach.

Total variants returned = {variants_per_seed} × number of seeds. The
`verbatim` baseline is NOT one of the seeds and must NOT be produced — it
is added separately by the runner.

Return a QueryVariantsResponse containing the list of variants."""


_USER_PROMPT = """Generate {variants_per_seed} variants per seed, for a total of {total_variants} variants.

Query spec:
{query_spec_json}

Paradigm seeds (produce {variants_per_seed} variants for EACH of these,
each exploring a different broadening approach):
{paradigm_seeds_list}

Return a QueryVariantsResponse."""


# ---- Phase A: LLM variant generation ----

VARIANTS_PER_SEED = 3


def request_query_variants(
    query_spec: BaseModel,
    paradigm_seeds: List[str],
    variants_per_seed: int = VARIANTS_PER_SEED,
    chat_model: Optional[BaseChatModel] = None,
) -> List[_LLMVariantOutput]:
    total_expected = variants_per_seed * len(paradigm_seeds)
    _log_debug(
        f"LLM call: model={DEFAULT_MODEL}, "
        f"seeds={paradigm_seeds}, variants_per_seed={variants_per_seed}, "
        f"total_expected={total_expected}"
    )

    started = datetime.now(timezone.utc)
    response = call_structured(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=_USER_PROMPT,
        output_schema=_QueryVariantsResponse,
        template_args={
            "variants_per_seed": variants_per_seed,
            "total_variants": total_expected,
            "query_spec_json": query_spec.model_dump_json(indent=2),
            "paradigm_seeds_list": "\n".join(f"- {s}" for s in paradigm_seeds),
        },
        model=DEFAULT_MODEL,
        chat_model=chat_model,
    )
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    _log_debug(f"LLM returned {len(response.variants)} variants in {elapsed:.1f}s")

    if len(response.variants) != total_expected:
        _log_warn(
            f"LLM returned {len(response.variants)} variants but {total_expected} were requested "
            f"(seeds={paradigm_seeds}, variants_per_seed={variants_per_seed})"
        )

    return response.variants


# ---- SERP: same client experiment.py uses ----

def make_retrieval_client() -> BrightDataGoogleSERPRetrievalClient:
    return BrightDataGoogleSERPRetrievalClient(
        token=None,
        serp_zone=None,
        auto_create_zones=True,
        default_location=SERP_LOCATION,
        default_language=SERP_LANGUAGE,
        default_device=SERP_DEVICE,
    )


def serp_search(
    client: BrightDataGoogleSERPRetrievalClient,
    query: str,
    n: int = SERP_RESULTS_PER_VARIANT,
) -> List[RetrievedCandidate]:
    _log_debug(f"SERP call: n={n}, location={SERP_LOCATION}, lang={SERP_LANGUAGE}, device={SERP_DEVICE}")
    _log_debug(f"SERP query: {query!r}")
    started = datetime.now(timezone.utc)
    candidates = client.search_sync(
        query=query,
        result_count=n,
        location=SERP_LOCATION,
        language=SERP_LANGUAGE,
        device=SERP_DEVICE,
    )
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    _log_debug(f"SERP returned {len(candidates)} candidates in {elapsed:.1f}s")
    if not candidates:
        _log_warn(f"SERP returned 0 candidates for query: {query!r}")
    return candidates


def candidate_to_serp_result(c: RetrievedCandidate) -> ExpansionSerpResult:
    """Convert one RetrievedCandidate dataclass into an ExpansionSerpResult.

    Judge result is left None — judging is not part of this script yet.
    """
    return ExpansionSerpResult(
        link=c.url or "",
        metadata={
            "rank": c.rank,
            "source_name": c.source_name,
            "title": c.title,
            **(c.structured_fields or {}),
        },
        snippet=c.snippet,
        llm_judge_result=None,
    )


# ---- Report save ----

def save_report(report: Dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"minimal4_{report['run_id']}.json"
    payload = json.dumps(report, indent=2, default=str)
    path.write_text(payload, encoding="utf-8")
    _log_debug(f"Wrote {len(payload):,} bytes to {path}")
    return path


# ---- __main__ ----

def main() -> None:
    started_at = datetime.now(timezone.utc)
    run_id = started_at.strftime("%Y%m%d_%H%M%S")

    spec = B2BQuerySpec(
        natural_query="VP Sales or Head of Sales at US cybersecurity SaaS startups in the United States",
        entity_type="person_profile",
        industry="cybersecurity SaaS",
        geography="United States",
        company_type="startup",
        role_title_family="sales_leadership",
        seniority_band="vp",
        department_or_function="sales",
    )

    # LLM-driven seeds only. `verbatim` is built deterministically in Python
    # from spec.natural_query — no LLM call needed for it.
    seeds = [
        "title_broadening",
        "industry_broadening",
        "geography_broadening",
        "combined_broadening",
    ]

    expected_llm_count = VARIANTS_PER_SEED * len(seeds)
    print(f"Phase A — generating variants via LLM ({VARIANTS_PER_SEED} per seed × {len(seeds)} seeds = {expected_llm_count} expected)...")
    llm_variants = request_query_variants(
        query_spec=spec, paradigm_seeds=seeds, variants_per_seed=VARIANTS_PER_SEED
    )
    print(f"  got {len(llm_variants)} variants from LLM")

    # The verbatim baseline is built in Python — no LLM call needed.
    verbatim_variant = _LLMVariantOutput(
        seeds=["verbatim"],
        query=spec.natural_query,
        rationale="Baseline: the natural query without any broadening.",
    )
    all_variants = [verbatim_variant, *llm_variants]
    print(f"  + 1 verbatim baseline = {len(all_variants)} total variants\n")

    print(f"Phase B — running SERP per variant ({SERP_RESULTS_PER_VARIANT} results each)...\n")
    client = make_retrieval_client()

    expansion_variants: List[ExpansionVariant] = []

    for i, v in enumerate(all_variants, 1):
        print(f"[{i}/{len(all_variants)}] seeds={v.seeds}")
        print(f"      query: {v.query}")

        if " AND " in v.query:
            _log_warn(
                f"Variant query contains literal 'AND' between phrases — "
                f"Google may parse this as a noisy token. Variant: {v.seeds}"
            )

        serp_results: List[ExpansionSerpResult] = []
        try:
            candidates = serp_search(client, v.query, n=SERP_RESULTS_PER_VARIANT)
        except Exception as exc:
            _log_warn(f"SERP exception for variant {v.seeds}: {exc}")
            print(f"      SERP error: {exc}\n")
            expansion_variants.append(
                ExpansionVariant(
                    seeds=v.seeds, query=v.query, rationale=v.rationale, serp_results=[]
                )
            )
            continue

        for c in candidates[:SERP_RESULTS_PER_VARIANT]:
            result = candidate_to_serp_result(c)
            serp_results.append(result)
            title = (c.title or "").strip()
            print(f"        {c.rank}. {result.link or '(no url)'}")
            if title:
                print(f"           {title}")

        expansion_variants.append(
            ExpansionVariant(
                seeds=v.seeds,
                query=v.query,
                rationale=v.rationale,
                serp_results=serp_results,
            )
        )
        print()

    completed_at = datetime.now(timezone.utc)

    report: Dict[str, Any] = {
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "elapsed_seconds": (completed_at - started_at).total_seconds(),
        "query_spec": spec.model_dump(mode="json"),
        "paradigm_seeds": list(seeds),
        "variants_per_seed": VARIANTS_PER_SEED,
        "expected_llm_count": expected_llm_count,
        "actual_llm_count": len(llm_variants),
        "total_variants": len(all_variants),
        "serp_results_per_variant": SERP_RESULTS_PER_VARIANT,
        "serp_location": SERP_LOCATION,
        "serp_language": SERP_LANGUAGE,
        "serp_device": SERP_DEVICE,
        "variants": [v.model_dump(mode="json") for v in expansion_variants],
    }

    path = save_report(report)
    print(f"Report saved: {path}")


if __name__ == "__main__":
    main()
