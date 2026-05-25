"""SERP layer for the LLM-based expansion pipeline.

Thin wrapper around `BrightDataGoogleSERPRetrievalClient` so callers
don't have to know its construction args or its `search_sync` signature.

Public surface:

    make_retrieval_client()      -> BrightDataGoogleSERPRetrievalClient
    serp_search(client, q, n)    -> List[RetrievedCandidate]
    candidate_to_serp_result(c)  -> ExpansionSerpResult

Module-level constants set the default location / language / device /
top-N for the whole pipeline.

Importer's contract: the SDK src path must already be on `sys.path`
before this module is imported (entry points like
`b2b_vertical_expansion_and_serp.py` do that bootstrap at startup).
This module does not bootstrap on its own — matching the existing
convention used by `llm_call.py` / `schemas.py`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from retrieval import BrightDataGoogleSERPRetrievalClient, RetrievedCandidate

from schemas import ExpansionSerpResult
from utils import log_debug, log_warn


SERP_LOCATION = "United States"
SERP_LANGUAGE = "en"
SERP_DEVICE = "desktop"
SERP_RESULTS_PER_VARIANT = 5


def make_retrieval_client() -> BrightDataGoogleSERPRetrievalClient:
    """Construct the Bright Data Google SERP client with project defaults."""
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
    """Run one Google SERP query and return up to `n` candidates."""
    log_debug(
        f"SERP call: n={n}, location={SERP_LOCATION}, "
        f"lang={SERP_LANGUAGE}, device={SERP_DEVICE}"
    )
    log_debug(f"SERP query: {query!r}")
    started = datetime.now(timezone.utc)
    candidates = client.search_sync(
        query=query,
        result_count=n,
        location=SERP_LOCATION,
        language=SERP_LANGUAGE,
        device=SERP_DEVICE,
    )
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    log_debug(f"SERP returned {len(candidates)} candidates in {elapsed:.1f}s")
    if not candidates:
        log_warn(f"SERP returned 0 candidates for query: {query!r}")
    return candidates


def candidate_to_serp_result(c: RetrievedCandidate) -> ExpansionSerpResult:
    """Convert one `RetrievedCandidate` dataclass into an `ExpansionSerpResult`.

    `llm_judge_result` is left None — judging is a separate step (see
    `add_score.py` / `judge_logic.py`).
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
