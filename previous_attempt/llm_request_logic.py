"""LangChain request logic for OpenAI expansion generation.

This module calls OpenAI through LangChain and asks it to return the
`ExpansionOutputResult` Pydantic schema defined in `task/expansion_schemas.py`.

The important boundary:

- `ExpansionExperimentConfig` is runner-owned configuration.
- `ExpansionInputData` is input context supplied to the LLM.
- The LLM returns only `ExpansionOutputResult`.
"""

from __future__ import annotations

from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain_openai import ChatOpenAI
except ImportError as exc:  # pragma: no cover - depends on local environment
    ChatOpenAI = None  # type: ignore[assignment]
    _OPENAI_IMPORT_ERROR = exc
else:
    _OPENAI_IMPORT_ERROR = None

from previous_attempt.expansion_schemas import (
    CombinationExpansionDraft,
    ExpansionExperimentConfig,
    ExpansionInputData,
    ExpansionOutputResult,
)
from previous_attempt.expansion_paradigm_types import ExpansionCombination


DEFAULT_OPENAI_MODEL = "gpt-4o"


EXPANSION_SYSTEM_PROMPT = """You generate structured search-query expansions for b2b_contact_data.

Return only data that matches the provided structured output schema.

Rules:
- Do not return plain strings only.
- Do not change experiment configuration.
- Generate exactly the configured number of expansions.
- Use only allowed source lanes, entity types, evidence modes, target fields, and exclusions.
- Each expansion must include a query and a structured expansion_trace.
- target_fields are fields the query is trying to surface, not fields already proven by evidence.
- source_lane is the target source/page family for the query, not a retrieval tool.
- Keep constraints visible: show what was preserved and what was broadened.
- Do not target private contact details unless explicitly allowed.
- Avoid known B2B noise such as job postings, career advice, resume pages, HR/recruiting software pages, and generic HR blogs.
"""


EXPANSION_USER_PROMPT = """Create structured expansion output for this experiment.

Experiment config:
{config_json}

Expansion input data:
{input_data_json}

Return an ExpansionOutputResult object.
"""


def create_openai_chat_model(
    model: str = DEFAULT_OPENAI_MODEL,
    temperature: float = 0.0,
    **kwargs: Any,
) -> BaseChatModel:
    """Create the OpenAI chat model used for expansion generation.

    Requires `langchain-openai` and `OPENAI_API_KEY` in the environment.
    """

    if ChatOpenAI is None:
        raise ImportError(
            "langchain-openai is required for OpenAI requests. "
            "Install it and configure OPENAI_API_KEY."
        ) from _OPENAI_IMPORT_ERROR

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        **kwargs,
    )


def build_expansion_prompt() -> ChatPromptTemplate:
    """Build the prompt used for structured expansion generation."""

    return ChatPromptTemplate.from_messages(
        [
            ("system", EXPANSION_SYSTEM_PROMPT),
            ("user", EXPANSION_USER_PROMPT),
        ]
    )


def request_expansion_output(
    config: ExpansionExperimentConfig,
    input_data: ExpansionInputData,
    chat_model: Optional[BaseChatModel] = None,
) -> ExpansionOutputResult:
    """Call the LLM and return validated `ExpansionOutputResult`.

    `chat_model` is injectable so tests can pass a fake LangChain chat model.
    """

    model = chat_model or create_openai_chat_model(model=config.model)
    structured_model = model.with_structured_output(
        ExpansionOutputResult, method="function_calling"
    )
    chain = build_expansion_prompt() | structured_model

    result = chain.invoke(
        {
            "config_json": _model_to_json(config),
            "input_data_json": _model_to_json(input_data),
        }
    )

    if not isinstance(result, ExpansionOutputResult):
        return _validate_expansion_output_result(result)

    return result


async def arequest_expansion_output(
    config: ExpansionExperimentConfig,
    input_data: ExpansionInputData,
    chat_model: Optional[BaseChatModel] = None,
) -> ExpansionOutputResult:
    """Async version of `request_expansion_output`."""

    model = chat_model or create_openai_chat_model(model=config.model)
    structured_model = model.with_structured_output(
        ExpansionOutputResult, method="function_calling"
    )
    chain = build_expansion_prompt() | structured_model

    result = await chain.ainvoke(
        {
            "config_json": _model_to_json(config),
            "input_data_json": _model_to_json(input_data),
        }
    )

    if not isinstance(result, ExpansionOutputResult):
        return _validate_expansion_output_result(result)

    return result


COMBINATION_SYSTEM_PROMPT = """You translate ONE pre-built expansion combination into ONE Google search query string for b2b_contact_data.

You receive:
- An original user query.
- A combination object that fixes: paradigms, entity_type, discovery_flow, source_lane, syntax_strategy, exclusion_strength, target_fields, exclusions, industry, geography, seniority, etc.

You return:
- One concrete `query` string that encodes the combination directly in the query text.
- A brief expansion trace: preserved_constraints, broadened_constraints, broadening_axis, rationale, risk_notes.

You do NOT pick entity_type, source_lane, syntax_strategy, paradigms, or any parameter values. Those are already fixed in the combination. Your only creative output is the query string and the trace narrative.

HARD LIMITS (apply to every query, regardless of combination):

- The final query MUST be UNDER 32 tokens. Google ignores everything past about 32 tokens, so longer queries lose the most-distinctive terms. Count site:, OR, and each -term as one token each.
- The final query MUST have AT MOST 2 negative terms, even if exclusion_strength is "strict". Two well-chosen negatives outperform a long list. Google de-weights negatives past ~2-3.
- When using OR, the alternatives MUST be wrapped in parentheses. Example: ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" -- WRONG: "VP Sales" OR "Head of Sales" "cybersecurity SaaS" (Google parses this as "VP Sales" OR ("Head of Sales" AND "cybersecurity SaaS")).

ENCODING RULES (apply all that match the combination):

1. source_lane controls the site: operator:
   - linkedin_person    -> site:linkedin.com/in
   - linkedin_company   -> site:linkedin.com/company
   - crunchbase_person  -> site:crunchbase.com/person
   - crunchbase_company -> site:crunchbase.com/organization
   - company_team_page  -> no site:; include inurl:team OR inurl:about hint
   - general_web        -> no site: operator

2. syntax_strategy is the dominant mechanic of the query:
   - site_operator    -> MUST start with the site: prefix from rule 1.
   - boolean_or       -> wrap role/title alternatives in parentheses: ("VP Sales" OR "Head of Sales"). Parentheses are REQUIRED.
   - negative_terms   -> use - prefixed exclusions (see rule 3) prominently.
   - quoted_phrase    -> wrap key multi-word phrases in double quotes.
   - exact_title      -> wrap the exact target title in double quotes.
   - natural_language -> plain words, no operators.

3. exclusion_strength sets the number of negative tokens, capped at 2 total:
   - light    -> 1 negative.
   - moderate -> 1-2 negatives.
   - strict   -> 2 negatives, well-chosen for the source_lane.
   Pick AT MOST 2 negatives total from the mappings below; choose the ones most likely to remove noise for THIS source_lane. Do not include every example.
     job_postings                    -> -jobs
     career_advice                   -> -"career advice"
     resume_templates                -> -resume
     hr_software_pages               -> -workday
     recruiting_software_pages       -> -recruiter
     staffing_agency_marketing_pages -> -staffing
     generic_hr_blogs                -> -blog
     unsupported_lead_directories    -> -zoominfo

4. Always quote multi-word industry and geography phrases. Example: "cybersecurity SaaS" "United States".

5. Preserve every constraint visible in the combination (industry, geography, role_title_family, seniority_band, department_or_function). If you broaden one, record it in broadened_constraints + broadening_axis. Otherwise list it in preserved_constraints.

6. Do not invent enum values. Do not return more than one query. Do not include alternative queries separated by commas. Do not target private contact details (email, phone) unless explicitly allowed.
"""


COMBINATION_USER_PROMPT = """Translate this combination into one Google search query.

Original user query:
{original_query}

Combination (paradigms + parameters):
{combination_json}

Return ONE CombinationExpansionDraft.
"""


def build_combination_prompt() -> ChatPromptTemplate:
    """Build the prompt used for one-combination query rendering."""

    return ChatPromptTemplate.from_messages(
        [
            ("system", COMBINATION_SYSTEM_PROMPT),
            ("user", COMBINATION_USER_PROMPT),
        ]
    )


def request_expansion_for_combination(
    original_query: str,
    combination: ExpansionCombination,
    model: str = DEFAULT_OPENAI_MODEL,
    chat_model: Optional[BaseChatModel] = None,
) -> CombinationExpansionDraft:
    """Ask the LLM to render one combination into a concrete query draft."""

    llm = chat_model or create_openai_chat_model(model=model)
    structured_llm = llm.with_structured_output(
        CombinationExpansionDraft, method="function_calling"
    )
    chain = build_combination_prompt() | structured_llm

    result = chain.invoke(
        {
            "original_query": original_query,
            "combination_json": _model_to_json(combination),
        }
    )

    return _validate_combination_draft(result)


async def arequest_expansion_for_combination(
    original_query: str,
    combination: ExpansionCombination,
    model: str = DEFAULT_OPENAI_MODEL,
    chat_model: Optional[BaseChatModel] = None,
) -> CombinationExpansionDraft:
    """Async version of `request_expansion_for_combination`."""

    llm = chat_model or create_openai_chat_model(model=model)
    structured_llm = llm.with_structured_output(
        CombinationExpansionDraft, method="function_calling"
    )
    chain = build_combination_prompt() | structured_llm

    result = await chain.ainvoke(
        {
            "original_query": original_query,
            "combination_json": _model_to_json(combination),
        }
    )

    return _validate_combination_draft(result)


def _validate_combination_draft(value: Any) -> CombinationExpansionDraft:
    if isinstance(value, CombinationExpansionDraft):
        return value
    if hasattr(CombinationExpansionDraft, "model_validate"):
        return CombinationExpansionDraft.model_validate(value)
    if hasattr(CombinationExpansionDraft, "parse_obj"):
        return CombinationExpansionDraft.parse_obj(value)
    raise TypeError("CombinationExpansionDraft has no Pydantic validator")


def _model_to_json(model: Any) -> str:
    """Serialize Pydantic v2/v1 models to JSON."""

    if hasattr(model, "model_dump_json"):
        return model.model_dump_json(indent=2)

    if hasattr(model, "json"):
        return model.json(indent=2)

    raise TypeError(f"Object is not a supported Pydantic model: {type(model)!r}")


def _validate_expansion_output_result(value: Any) -> ExpansionOutputResult:
    """Validate `ExpansionOutputResult` on Pydantic v2 or v1."""

    if hasattr(ExpansionOutputResult, "model_validate"):
        return ExpansionOutputResult.model_validate(value)

    if hasattr(ExpansionOutputResult, "parse_obj"):
        return ExpansionOutputResult.parse_obj(value)

    raise TypeError("ExpansionOutputResult does not expose a Pydantic validator")
