"""Minimal runnable example of request_query_variants + per-variant SERP.

For each LLM-produced variant, run Bright Data Google SERP and print the
top 5 result URLs. Also write the full result as JSON to
`outputs/minimal2_<UTC>.json`.

Run:
    python src/expansion/llm_based/minimal2.py

Requires .env with OPENAI_API_KEY and BRIGHTDATA_API_TOKEN.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, is_dataclass
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
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from retrieval import BrightDataGoogleSERPRetrievalClient, RetrievedCandidate  # noqa: E402


load_dotenv()


DEFAULT_MODEL = "gpt-4o"
SERP_LOCATION = "United States"
SERP_LANGUAGE = "en"
SERP_DEVICE = "desktop"
SERP_RESULTS_PER_VARIANT = 5
OUTPUT_DIR = PROJECT_ROOT / "outputs"


# ---- Pydantic schemas ----

class QueryVariant(BaseModel):
    variant_id: str = Field(..., description="Unique id like 'var_001_title_broadening'.")
    seeds: List[str] = Field(..., description="Which seed paradigms shaped this variant.")
    query_body: str = Field(..., description="Google query body, no site: prefix, no -keyword exclusions.")
    rationale: str = Field(..., description="One-sentence explanation.")


class _QueryVariantsResponse(BaseModel):
    variants: List[QueryVariant]


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


# ---- Phase A: LLM variant generation ----

def request_query_variants(
    query_spec: BaseModel,
    paradigm_seeds: List[str],
    num_variants: int = 8,
    chat_model: Optional[BaseChatModel] = None,
) -> List[QueryVariant]:
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


# ---- Serialization ----

def to_serializable(value: Any) -> Any:
    """Recursively convert Pydantic / dataclass / list / dict to JSON-safe values."""
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {k: to_serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]
    return value


def save_report(report: Dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"minimal2_{report['run_id']}.json"
    output_path.write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    return output_path


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

    seeds = [
        "verbatim",
        "title_broadening",
        "industry_broadening",
        "geography_broadening",
        "combined_broadening",
    ]

    print("Phase A — generating variants via LLM...")
    variants = request_query_variants(
        query_spec=spec, paradigm_seeds=seeds, num_variants=8
    )
    print(f"  got {len(variants)} variants\n")

    print(f"Phase B — running SERP per variant ({SERP_RESULTS_PER_VARIANT} results each)...\n")
    client = make_retrieval_client()

    variant_entries: List[Dict[str, Any]] = []

    for i, v in enumerate(variants, 1):
        print(f"[{i}/{len(variants)}] {v.variant_id}  seeds={v.seeds}")
        print(f"      query: {v.query_body}")

        entry: Dict[str, Any] = {
            **to_serializable(v),
            "serp_results": [],
            "serp_error": None,
        }

        try:
            candidates = serp_search(client, v.query_body, n=SERP_RESULTS_PER_VARIANT)
        except Exception as exc:
            print(f"      SERP error: {exc}\n")
            entry["serp_error"] = str(exc)
            variant_entries.append(entry)
            continue

        for c in candidates[:SERP_RESULTS_PER_VARIANT]:
            url = c.url or "(no url)"
            title = (c.title or "").strip()[:80]
            print(f"        {c.rank}. {url}")
            if title:
                print(f"           {title}")
            entry["serp_results"].append(to_serializable(c))

        variant_entries.append(entry)
        print()

    completed_at = datetime.now(timezone.utc)

    report: Dict[str, Any] = {
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "elapsed_seconds": (completed_at - started_at).total_seconds(),
        "query_spec": to_serializable(spec),
        "paradigm_seeds": list(seeds),
        "num_variants_requested": 8,
        "num_variants_received": len(variants),
        "serp_results_per_variant": SERP_RESULTS_PER_VARIANT,
        "serp_location": SERP_LOCATION,
        "serp_language": SERP_LANGUAGE,
        "serp_device": SERP_DEVICE,
        "variants": variant_entries,
    }

    output_path = save_report(report)
    print(f"Report saved: {output_path}")


if __name__ == "__main__":
    main()
