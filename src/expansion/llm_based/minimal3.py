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

import sys
from pathlib import Path
from typing import List, Optional


# ---- sys.path bootstrap (same shape as experiment.py / config.py) ----

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SDK_SRC = Path("/Users/ns/Desktop/projects/sdk-python/src")

for _path in (PROJECT_ROOT, SDK_SRC):
    p = str(_path)
    if p not in sys.path:
        sys.path.insert(0, p)


from dotenv import load_dotenv  # noqa: E402
from langchain_core.language_models.chat_models import BaseChatModel  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from retrieval import BrightDataGoogleSERPRetrievalClient, RetrievedCandidate  # noqa: E402

from schemas import ExpansionSerpResult, ExpansionVariant  # noqa: E402


load_dotenv()


DEFAULT_MODEL = "gpt-4o"
SERP_LOCATION = "United States"
SERP_LANGUAGE = "en"
SERP_DEVICE = "desktop"
SERP_RESULTS_PER_VARIANT = 5


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

Given a query spec (JSON) and a list of paradigm seeds, produce exactly N query variants.

Each variant must:
- Preserve the spec's constraints (industry, geography, seniority, role/title family).
- Be shaped by one or more of the listed seed paradigms.
- Use Google syntax for broadenings: ("A" OR "B" OR "C") with parentheses.
- Quote multi-word phrases.
- NOT include site: operators.
- NOT include negative -keyword exclusions.
- List the seeds it embodies in `seeds`.
- Include a one-sentence rationale.

One variant with seed "verbatim" must be included (the baseline — natural query, no broadening).

Return a QueryVariantsResponse containing the list of variants."""


_USER_PROMPT = """Generate {num_variants} query variants.

Query spec:
{query_spec_json}

Paradigm seeds (use these as a menu of transformation styles):
{paradigm_seeds_list}

Return a QueryVariantsResponse."""


# ---- Phase A: LLM variant generation ----

def request_query_variants(
    query_spec: BaseModel,
    paradigm_seeds: List[str],
    num_variants: int = 8,
    chat_model: Optional[BaseChatModel] = None,
) -> List[_LLMVariantOutput]:
    llm = chat_model or ChatOpenAI(model=DEFAULT_MODEL, temperature=0.0)
    structured = llm.with_structured_output(
        _QueryVariantsResponse, method="function_calling"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_PROMPT),
            ("user", _USER_PROMPT),
        ]
    )
    chain = prompt | structured

    response = chain.invoke(
        {
            "num_variants": num_variants,
            "query_spec_json": query_spec.model_dump_json(indent=2),
            "paradigm_seeds_list": "\n".join(f"- {s}" for s in paradigm_seeds),
        }
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
    return client.search_sync(
        query=query,
        result_count=n,
        location=SERP_LOCATION,
        language=SERP_LANGUAGE,
        device=SERP_DEVICE,
    )


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


# ---- __main__ ----

def main() -> None:
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

    seeds = [
        "verbatim",
        "title_broadening",
        "industry_broadening",
        "geography_broadening",
        "combined_broadening",
    ]

    print("Phase A — generating variants via LLM...")
    llm_variants = request_query_variants(
        query_spec=spec, paradigm_seeds=seeds, num_variants=8
    )
    print(f"  got {len(llm_variants)} variants\n")

    print(f"Phase B — running SERP per variant ({SERP_RESULTS_PER_VARIANT} results each)...\n")
    client = make_retrieval_client()

    expansion_variants: List[ExpansionVariant] = []

    for i, v in enumerate(llm_variants, 1):
        print(f"[{i}/{len(llm_variants)}] seeds={v.seeds}")
        print(f"      query: {v.query}")

        serp_results: List[ExpansionSerpResult] = []
        try:
            candidates = serp_search(client, v.query, n=SERP_RESULTS_PER_VARIANT)
        except Exception as exc:
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


if __name__ == "__main__":
    main()
