"""Minimal runnable example of request_query_variants.

Run:
    python src/expansion/llm_based/minimal.py
"""

from __future__ import annotations

from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


load_dotenv()


DEFAULT_MODEL = "gpt-4o"


# ---- Pydantic schemas ----

class QueryVariant(BaseModel):
    variant_id: str = Field(..., description="Unique id like 'var_001_title_broadening'.")
    seeds: List[str] = Field(..., description="Which seed paradigms shaped this variant.")
    query_body: str = Field(..., description="Google query body, no site: prefix, no -keyword exclusions.")
    rationale: str = Field(..., description="One-sentence explanation.")


class _QueryVariantsResponse(BaseModel):
    variants: List[QueryVariant]


# Example query spec (any Pydantic BaseModel works — this is one shape).

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
- Have a variant_id of the form var_<NNN>_<primary_seed>.
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


# ---- The function ----

def request_query_variants(
    query_spec: BaseModel,
    paradigm_seeds: List[str],
    num_variants: int = 8,
    chat_model: Optional[BaseChatModel] = None,
) -> List[QueryVariant]:
    """Generate semantic query variants via one LLM call.

    `query_spec` is any Pydantic BaseModel; the function only calls
    `.model_dump_json()` on it. `paradigm_seeds` is a list of seed
    identifiers (plain strings) the LLM uses as a transformation menu.
    """
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

    variants = request_query_variants(
        query_spec=spec, paradigm_seeds=seeds, num_variants=8
    )

    print(f"\nReceived {len(variants)} variants:\n")
    for i, v in enumerate(variants, 1):
        print(f"[{i}] {v.variant_id}")
        print(f"    seeds:     {v.seeds}")
        print(f"    query:     {v.query_body}")
        print(f"    rationale: {v.rationale}")
        print()


if __name__ == "__main__":
    main()
