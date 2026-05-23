"""Bright Data Google SERP retrieval client.

This client intentionally uses the public SDK flow:

`BrightDataClient(...).search.google(...)`

That public method internally delegates to the SDK Google SERP service in
`/Users/ns/Desktop/projects/sdk-python/src/brightdata/serp/google.py`.

It does not call Bright Data HTTP endpoints directly and does not use other
search engines or Discover API paths.
"""

from __future__ import annotations

import asyncio
from typing import Any, List, Optional

from brightdata import BrightDataClient
from brightdata.models import SearchResult

from .schemas import RetrievedCandidate


BRIGHT_DATA_GOOGLE_SERP_SOURCE = "bright_data_google_serp"


class BrightDataGoogleSERPRetrievalError(RuntimeError):
    """Raised when Bright Data Google SERP retrieval fails."""


class BrightDataGoogleSERPRetrievalClient:
    """Run Google SERP retrieval through `BrightDataClient.search.google`."""

    def __init__(
        self,
        token: Optional[str] = None,
        serp_zone: Optional[str] = None,
        timeout: int = 30,
        auto_create_zones: bool = True,
        default_location: Optional[str] = None,
        default_language: str = "en",
        default_device: str = "desktop",
    ) -> None:
        self.token = token
        self.serp_zone = serp_zone
        self.timeout = timeout
        self.auto_create_zones = auto_create_zones
        self.default_location = default_location
        self.default_language = default_language
        self.default_device = default_device

    async def search(
        self,
        query: str,
        result_count: int = 10,
        location: Optional[str] = None,
        language: Optional[str] = None,
        device: Optional[str] = None,
        zone: Optional[str] = None,
        **google_serp_kwargs: Any,
    ) -> List[RetrievedCandidate]:
        """Search Google SERP and return normalized benchmark candidates."""

        async with BrightDataClient(
            token=self.token,
            timeout=self.timeout,
            serp_zone=self.serp_zone,
            auto_create_zones=self.auto_create_zones,
        ) as client:
            search_result = await client.search.google(
                query=query,
                zone=zone or client.serp_zone,
                location=location if location is not None else self.default_location,
                language=language or self.default_language,
                device=device or self.default_device,
                num_results=result_count,
                **google_serp_kwargs,
            )

        if not isinstance(search_result, SearchResult):
            raise BrightDataGoogleSERPRetrievalError(
                "Expected a single SearchResult from BrightDataClient.search.google()."
            )

        return normalize_google_serp_result(search_result)

    def search_sync(
        self,
        query: str,
        result_count: int = 10,
        location: Optional[str] = None,
        language: Optional[str] = None,
        device: Optional[str] = None,
        zone: Optional[str] = None,
        **google_serp_kwargs: Any,
    ) -> List[RetrievedCandidate]:
        """Synchronous wrapper for scripts that do not already run an event loop."""

        return asyncio.run(
            self.search(
                query=query,
                result_count=result_count,
                location=location,
                language=language,
                device=device,
                zone=zone,
                **google_serp_kwargs,
            )
        )


def normalize_google_serp_result(
    search_result: SearchResult,
) -> List[RetrievedCandidate]:
    """Convert SDK `SearchResult.data` into benchmark retrieval candidates."""

    if not search_result.success:
        raise BrightDataGoogleSERPRetrievalError(
            search_result.error or "Google SERP search failed."
        )

    candidates: List[RetrievedCandidate] = []

    for index, item in enumerate(search_result.data or [], start=1):
        rank = _coerce_rank(item.get("position"), fallback=index)
        candidates.append(
            RetrievedCandidate(
                rank=rank,
                source_name=BRIGHT_DATA_GOOGLE_SERP_SOURCE,
                url=_optional_str(item.get("url")),
                title=_optional_str(item.get("title")),
                snippet=_optional_str(item.get("description")),
                structured_fields={
                    "displayed_url": item.get("displayed_url"),
                    "search_engine": search_result.search_engine,
                    "query": search_result.query,
                    "country": search_result.country,
                    "total_found": search_result.total_found,
                    "results_per_page": search_result.results_per_page,
                },
                raw=item,
            )
        )

    return candidates


def _coerce_rank(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    return text or None
