"""Normalized retrieval schemas used by the benchmark runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class RetrievedCandidate:
    """One normalized candidate returned by a retrieval method.

    This shape is intentionally provider-neutral so the evaluator can judge
    SERP, WSAPI, datasets, or Discover outputs later without changing the
    boolean judging prompt. For now, Bright Data Google SERP is the only
    implemented retrieval method.
    """

    rank: int
    source_name: str
    url: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    content: Optional[str] = None
    structured_fields: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)
