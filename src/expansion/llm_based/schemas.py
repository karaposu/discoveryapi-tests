"""Pydantic schemas for the LLM-based expansion + SERP + judge pipeline.

Three nested types:

    ExpansionVariant
      └─ serp_results: List[ExpansionSerpResult]
            └─ llm_judge_result: Optional[LLMJudgeResult]
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, computed_field


class LLMJudgeResult(BaseModel):
    """Per-candidate boolean judge output.

    `boolean_answers` aligns positionally with the questions in
    `original_questions`: `boolean_answers[i]` is the YES/NO verdict for
    the i-th question. `total_point` is a derived field — the sum of
    True values, kept consistent with `boolean_answers` automatically.
    """

    boolean_answers: List[bool] = Field(
        ..., description="True/False per question, in the order they appear in original_questions."
    )
    original_questions: str = Field(
        ..., description="The full judge prompt (or question list) as a string, for self-description."
    )

    @computed_field
    @property
    def total_point(self) -> int:
        """Sum of True values in `boolean_answers`. Range: 0 .. len(boolean_answers)."""
        return sum(1 for a in self.boolean_answers if a)


class ExpansionSerpResult(BaseModel):
    """One Google SERP result for an expansion variant."""

    link: str = Field(..., description="The result URL.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured SERP metadata (rank, displayed_url, country, etc.).",
    )
    snippet: Optional[str] = Field(
        default=None, description="Result snippet/description as returned by SERP."
    )
    llm_judge_result: Optional[LLMJudgeResult] = Field(
        default=None,
        description="Per-candidate judge output. None when judging is skipped.",
    )


class ExpansionVariant(BaseModel):
    """One LLM-generated semantic expansion + its SERP candidates."""

    seeds: List[str] = Field(
        ..., description="Which seed paradigms shaped this variant (e.g. 'title_broadening')."
    )
    query: str = Field(
        ..., description="The Google query body — no site: prefix, no -keyword exclusions."
    )
    rationale: str = Field(
        ..., description="One-sentence explanation of what this variant is doing."
    )
    serp_results: List[ExpansionSerpResult] = Field(
        default_factory=list,
        description="The SERP results for this variant's query, top-N from Bright Data Google.",
    )
