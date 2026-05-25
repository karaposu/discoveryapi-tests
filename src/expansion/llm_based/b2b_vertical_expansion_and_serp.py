"""B2B-vertical query expansion + per-variant Google SERP.

Phase A: ask the LLM for paradigm-seeded variants of a `B2BQuerySpec`.
Phase B: for each variant, run a Bright Data Google SERP query and keep
the top N results.

Uses the shared `schemas.py` types (`ExpansionVariant`,
`ExpansionSerpResult`). Judge scoring is NOT done here — every
`ExpansionSerpResult.llm_judge_result` is left as `None`. Run
`add_score.py` on the saved report to populate them.

Run:
    python src/expansion/llm_based/b2b_vertical_expansion_and_serp.py

Requires .env with OPENAI_API_KEY and BRIGHTDATA_API_TOKEN.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


# ---- sys.path bootstrap (same shape as experiment.py / config.py) ----

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SDK_SRC = Path("/Users/ns/Desktop/projects/sdk-python/src")

for _path in (PROJECT_ROOT, SDK_SRC):
    p = str(_path)
    if p not in sys.path:
        sys.path.insert(0, p)


from dotenv import load_dotenv  # noqa: E402

from schemas import (  # noqa: E402
    B2BQuerySpec,
    ExpansionSerpResult,
    ExpansionVariant,
    LLMVariantOutput,
)
from serp import (  # noqa: E402
    SERP_DEVICE,
    SERP_LANGUAGE,
    SERP_LOCATION,
    SERP_RESULTS_PER_VARIANT,
    candidate_to_serp_result,
    make_retrieval_client,
    serp_search,
)
from utils import log_warn, save_report  # noqa: E402
from variant_generation import VARIANTS_PER_SEED, request_query_variants  # noqa: E402


load_dotenv()


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
    verbatim_variant = LLMVariantOutput(
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
            log_warn(
                f"Variant query contains literal 'AND' between phrases — "
                f"Google may parse this as a noisy token. Variant: {v.seeds}"
            )

        serp_results: List[ExpansionSerpResult] = []
        try:
            candidates = serp_search(client, v.query, n=SERP_RESULTS_PER_VARIANT)
        except Exception as exc:
            log_warn(f"SERP exception for variant {v.seeds}: {exc}")
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

    path = save_report(report, prefix="b2b_vertical_expansion_and_serp")
    print(f"Report saved: {path}")


if __name__ == "__main__":
    main()
