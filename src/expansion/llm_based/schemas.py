"""Pydantic schemas for the LLM-based expansion + SERP + judge pipeline.

Domain types (used in reports + runtime data):

    B2BQuerySpec                            # input: structured form of user query
    ExpansionVariant                        # output: one variant + its SERP results
      └─ serp_results: List[ExpansionSerpResult]
            └─ llm_judge_result: Optional[LLMJudgeResult]

LLM-facing types (used as `with_structured_output` schemas):

    LLMVariantOutput                        # the slim shape the LLM produces per variant
    LLMVariantsResponse                     # wrapper: variants: List[LLMVariantOutput]
    JudgeResponse                           # wrapper: boolean_answers: List[bool]

The LLM-facing types are kept here (rather than inlined in their callers)
so that any code building or consuming the pipeline can refer to one
canonical schema module.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, computed_field


# ============================================================================
# Domain types — query input
# ============================================================================

class B2BQuerySpec(BaseModel):
    """Structured form of a B2B contact-discovery query.

    One instance per run; consumed by Phase A (variant generation) and by
    downstream layers (judge, scoring). All fields except natural_query
    are optional — leave them None when not applicable to the query.
    """

    natural_query: str = Field(
        ..., description="The original natural-language query as written by the user."
    )
    entity_type: str = Field(
        ...,
        description=(
            "What kind of result is sought: 'person_profile', 'company_profile', "
            "or 'mixed_person_company'."
        ),
    )
    industry: Optional[str] = None
    geography: Optional[str] = None
    company_type: Optional[str] = None
    company_size_or_stage: Optional[str] = None
    role_title_family: Optional[str] = None
    seniority_band: Optional[str] = None
    department_or_function: Optional[str] = None


# ============================================================================
# Domain types — pipeline output
# ============================================================================

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


# ============================================================================
# LLM-facing types — structured-output response shapes
# ============================================================================

class LLMVariantOutput(BaseModel):
    """LLM-produced subset of an ExpansionVariant — no serp_results.

    Kept as a separate shape (instead of having the LLM return
    ExpansionVariant directly) because ExpansionVariant.serp_results is
    filled in by Phase B (Python + SERP). Letting the LLM see that field
    in the structured-output schema risks the model hallucinating SERP
    rows.
    """

    seeds: List[str] = Field(
        ..., description="Which seed paradigms shaped this variant."
    )
    query: str = Field(
        ...,
        description=(
            "The Google query body — no site: prefix, no -keyword exclusions."
        ),
    )
    rationale: str = Field(
        ..., description="One-sentence explanation of what this variant is doing."
    )


class LLMVariantsResponse(BaseModel):
    """The full LLM response for Phase A: a list of LLMVariantOutput.

    LangChain's `with_structured_output` returns a single object; this
    wrapper holds the list so the caller can unwrap `.variants`.
    """

    variants: List[LLMVariantOutput]


class JudgeResponse(BaseModel):
    """The full LLM response for one judge call.

    `boolean_answers` aligns positionally with the question list the
    caller passed in. The caller promotes this into a full `LLMJudgeResult`
    by attaching the original questions string.
    """

    boolean_answers: List[bool] = Field(
        ...,
        description=(
            "One True/False per question, in the order given in the system prompt. "
            "Length must equal the number of questions."
        ),
    )
