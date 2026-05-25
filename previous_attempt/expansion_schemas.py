"""Pydantic schemas for LLM expansion prompt experiments.

These models define the lifecycle boundary for Task 1:

- `ExpansionExperimentConfig` is owned by the benchmark runner.
- `ExpansionInputData` is input context supplied to the LLM.
- `ExpansionOutputResult` is the object the LLM returns.
- `ExpansionOutputItem` is one generated search expansion.

Retrieval outputs, relevance labels, metrics, field credits, and human audit
records deliberately stay outside this module.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


B2BContactDataCategoryName = Literal["b2b_contact_data"]


class ExpansionOutputEntityType(str, Enum):
    """Contract-aligned entity types an expansion can target."""

    person_profile = "person_profile"
    company_profile = "company_profile"
    mixed_person_company = "mixed_person_company"


class ExpansionOutputSourceLane(str, Enum):
    """Source-family target, not a retrieval tool result."""

    linkedin_person = "linkedin_person"
    linkedin_company = "linkedin_company"
    crunchbase_person = "crunchbase_person"
    crunchbase_company = "crunchbase_company"
    company_team_page = "company_team_page"
    general_web = "general_web"


class ExpansionOutputEvidenceMode(str, Enum):
    """Expected evidence mode the expansion is trying to surface."""

    snippet_only = "snippet_only"
    content = "content"
    structured_enrichment = "structured_enrichment"


class ExpansionOutputParadigm(str, Enum):
    """Paradigm families used to explain how an expansion was produced."""

    intent_and_terminology = "intent_and_terminology"
    entity_targeting = "entity_targeting"
    discovery_flow = "discovery_flow"
    source_lane_targeting = "source_lane_targeting"
    constraint_handling = "constraint_handling"
    field_and_evidence_targeting = "field_and_evidence_targeting"
    noise_control = "noise_control"
    query_syntax_shaping = "query_syntax_shaping"
    tool_and_evidence_mode_targeting = "tool_and_evidence_mode_targeting"


class ExpansionOutputDiscoveryFlow(str, Enum):
    """The intended discovery path for a generated expansion."""

    person_first = "person_first"
    company_first = "company_first"
    company_then_person = "company_then_person"
    mixed = "mixed"


class ExpansionOutputBroadeningAxis(str, Enum):
    """Which original query constraint was broadened, if any."""

    none = "none"
    title = "title"
    industry = "industry"
    geography = "geography"
    source = "source"
    company_type = "company_type"
    seniority = "seniority"


class ExpansionQuerySyntaxStrategy(str, Enum):
    """How the query text is expressed for retrieval."""

    natural_language = "natural_language"
    quoted_phrase = "quoted_phrase"
    site_operator = "site_operator"
    boolean_or = "boolean_or"
    negative_terms = "negative_terms"
    exact_title = "exact_title"


class ExpansionInputConstraintValue(BaseModel):
    """One original constraint supplied to the LLM as expansion input."""

    name: str
    value: str
    note: Optional[str] = None


class ExpansionOutputConstraintValue(BaseModel):
    """One preserved or broadened constraint reported by LLM output."""

    name: str
    value: str
    note: Optional[str] = None


class ExpansionOutputTrace(BaseModel):
    """Structured explanation of how a generated query was expanded.

    This is required because query text alone does not tell us whether a prompt
    changed source lane, broadened title wording, preserved geography, or used
    a different expansion recipe.
    """

    recipe_name: str
    paradigms: List[ExpansionOutputParadigm]
    preserved_constraints: List[ExpansionOutputConstraintValue] = Field(
        default_factory=list
    )
    broadened_constraints: List[ExpansionOutputConstraintValue] = Field(
        default_factory=list
    )
    broadening_axis: ExpansionOutputBroadeningAxis = ExpansionOutputBroadeningAxis.none
    rationale: str


class ExpansionExperimentConfig(BaseModel):
    """Runner-owned fixed settings for a prompt comparison.

    The LLM should not generate this model. It fixes the comparison settings so
    prompt variants are evaluated against the same constraints.
    """

    category: B2BContactDataCategoryName = "b2b_contact_data"
    model: str
    prompt_version: str
    num_expansions: int
    allowed_entity_types: List[ExpansionOutputEntityType]
    allowed_source_lanes: List[ExpansionOutputSourceLane]
    allowed_evidence_modes: List[ExpansionOutputEvidenceMode]
    allowed_target_fields: List[str]
    allowed_exclusions: List[str] = Field(default_factory=list)
    max_query_length: Optional[int] = None
    fixed_retrieval_method: Optional[str] = None
    fixed_result_count: Optional[int] = None
    locale: Optional[str] = None


class ExpansionInputData(BaseModel):
    """Input context supplied to the LLM for the expansion step.

    This is not retrieved source data from LinkedIn, Crunchbase, or the web.
    It is the original query and category context the LLM uses to generate
    expansions.
    """

    original_query: str
    normalized_intent: Optional[str] = None
    declared_constraints: List[ExpansionInputConstraintValue] = Field(
        default_factory=list
    )
    category_contract_ref: str = "task/b2b_contact_data_category_output_contract.py"
    expansion_paradigm_ref: str = "task/expansion_paradigm_types.py"
    allowed_source_lanes: List[ExpansionOutputSourceLane] = Field(default_factory=list)
    allowed_exclusions: List[str] = Field(default_factory=list)
    allowed_target_fields: List[str] = Field(default_factory=list)
    notes_for_llm: Optional[str] = None


class ExpansionOutputItem(BaseModel):
    """One typed search expansion returned by the LLM."""

    expansion_id: str
    entity_type: ExpansionOutputEntityType
    source_lane: ExpansionOutputSourceLane
    query: str
    target_fields: List[str]
    exclusions: List[str] = Field(default_factory=list)
    expansion_trace: ExpansionOutputTrace
    expected_evidence_mode: ExpansionOutputEvidenceMode
    risk_notes: List[str] = Field(default_factory=list)
    discovery_flow: Optional[ExpansionOutputDiscoveryFlow] = None
    syntax_strategy: Optional[ExpansionQuerySyntaxStrategy] = None
    enrichment_hint: Optional[str] = None
    diagnostic_purpose: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class ExpansionOutputResult(BaseModel):
    """LLM-returned result wrapper for one prompt run.

    The LLM should return this shape, not `ExpansionExperimentConfig` and not
    `ExpansionInputData`.
    """

    result_id: str
    category: B2BContactDataCategoryName = "b2b_contact_data"
    model: str
    prompt_version: str
    original_query: str
    expansions: List[ExpansionOutputItem]
    generation_notes: Optional[str] = None


class CombinationExpansionDraft(BaseModel):
    """LLM-returned draft for one pre-built expansion combination.

    The runner already knows the source_lane, entity_type, paradigms, and
    parameter values for the combination. The LLM only renders the concrete
    query string and a brief expansion trace; everything else is filled in
    by Python from the combination metadata. Keeping this object small
    minimizes hallucination and avoids redundant enum echoing.
    """

    query: str
    preserved_constraints: List[ExpansionOutputConstraintValue] = Field(
        default_factory=list
    )
    broadened_constraints: List[ExpansionOutputConstraintValue] = Field(
        default_factory=list
    )
    broadening_axis: ExpansionOutputBroadeningAxis = ExpansionOutputBroadeningAxis.none
    rationale: str
    risk_notes: List[str] = Field(default_factory=list)


class ExpansionExperimentRecord(BaseModel):
    """Optional runner-side record tying config, input, and LLM output.

    This is useful for logging, but it is not the object the LLM should return.
    """

    experiment_config: ExpansionExperimentConfig
    input_data: ExpansionInputData
    output_result: ExpansionOutputResult


EXAMPLE_EXPANSION_OUTPUT_RESULT = ExpansionOutputResult(
    result_id="b2b_sales_001_source_aware_v1",
    model="gpt-4o",
    prompt_version="source_aware_v1",
    original_query="heads of sales at US cybersecurity SaaS companies",
    expansions=[
        ExpansionOutputItem(
            expansion_id="exp_001",
            entity_type=ExpansionOutputEntityType.person_profile,
            source_lane=ExpansionOutputSourceLane.linkedin_person,
            query=(
                'site:linkedin.com/in ("Head of Sales" OR "VP Sales") '
                '"cybersecurity SaaS" "United States"'
            ),
            target_fields=[
                "person_name",
                "current_title",
                "current_company",
                "profile_or_source_url",
            ],
            exclusions=[
                "job_postings",
                "career_advice",
                "recruiting_software_pages",
            ],
            expansion_trace=ExpansionOutputTrace(
                recipe_name="Source-Aware Person-First",
                paradigms=[
                    ExpansionOutputParadigm.source_lane_targeting,
                    ExpansionOutputParadigm.discovery_flow,
                    ExpansionOutputParadigm.intent_and_terminology,
                    ExpansionOutputParadigm.noise_control,
                ],
                preserved_constraints=[
                    ExpansionOutputConstraintValue(
                        name="role", value="sales leadership"
                    ),
                    ExpansionOutputConstraintValue(
                        name="industry", value="cybersecurity SaaS"
                    ),
                    ExpansionOutputConstraintValue(
                        name="geography", value="United States"
                    ),
                ],
                broadened_constraints=[
                    ExpansionOutputConstraintValue(
                        name="title",
                        value="Head of Sales -> VP Sales",
                        note="Title wording broadened while preserving seniority.",
                    )
                ],
                broadening_axis=ExpansionOutputBroadeningAxis.title,
                rationale=(
                    "Targets LinkedIn person profiles and broadens title wording "
                    "while preserving industry and geography."
                ),
            ),
            expected_evidence_mode=ExpansionOutputEvidenceMode.snippet_only,
            risk_notes=[
                "May miss profiles that do not mention cybersecurity SaaS directly."
            ],
            discovery_flow=ExpansionOutputDiscoveryFlow.person_first,
            syntax_strategy=ExpansionQuerySyntaxStrategy.site_operator,
        )
    ],
)
