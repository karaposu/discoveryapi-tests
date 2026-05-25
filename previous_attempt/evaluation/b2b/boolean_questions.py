"""Boolean judge prompt for `b2b_contact_data` result evaluation.

The judge should answer narrow YES/NO questions. It should not produce
numeric scores. Benchmark code can convert these boolean labels into
relevance, field coverage, noise, and aggregate scores later.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, List, Literal, Optional, Tuple

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

try:
    from langchain_openai import ChatOpenAI
except ImportError as exc:  # pragma: no cover - depends on local environment
    ChatOpenAI = None  # type: ignore[assignment]
    _OPENAI_IMPORT_ERROR = exc
else:
    _OPENAI_IMPORT_ERROR = None


@dataclass(frozen=True)
class BooleanJudgeQuestion:
    """One auditable yes/no question for the B2B contact-data judge."""

    id: str
    question: str


B2BBooleanJudgeQuestionId = Literal[
    "is_b2b_contact_data_candidate",
    "matches_requested_entity_type",
    "satisfies_explicit_query_constraints",
    "exposes_core_identity_fields",
    "exposes_useful_extra_b2b_field",
    "credited_fields_visible_in_evidence",
    "suitable_professional_or_company_source",
    "shows_current_professional_or_company_context",
    "free_of_known_noise_page_types",
    "free_of_visible_wrong_match_failures",
]

B2BBooleanJudgeAnswerValue = Literal["YES", "NO"]


class B2BBooleanJudgeOutputAnswer(BaseModel):
    """One structured yes/no answer returned by the LLM judge."""

    question_id: B2BBooleanJudgeQuestionId
    answer: B2BBooleanJudgeAnswerValue


class B2BBooleanJudgeOutputResult(BaseModel):
    """Structured LLM judge output for the 10 B2B boolean questions."""

    answers: List[B2BBooleanJudgeOutputAnswer]


B2B_BOOLEAN_JUDGE_QUESTIONS: Tuple[BooleanJudgeQuestion, ...] = (
    BooleanJudgeQuestion(
        id="is_b2b_contact_data_candidate",
        question=(
            "Is this result a B2B contact-data candidate, not merely a "
            "generic article, product page, blog post, or topical page?"
        ),
    ),
    BooleanJudgeQuestion(
        id="matches_requested_entity_type",
        question=(
            "Does the result match the entity type requested or implied by "
            "the query: person, company, or mixed person-company?"
        ),
    ),
    BooleanJudgeQuestion(
        id="satisfies_explicit_query_constraints",
        question=(
            "Does the result satisfy the query's explicit constraints, such "
            "as role/title, industry, geography, seniority, company type, or "
            "company stage?"
        ),
    ),
    BooleanJudgeQuestion(
        id="exposes_core_identity_fields",
        question=(
            "Does the result expose the core identity fields required for its "
            "result type? For a person or mixed result, this means person "
            "name plus current title or current company plus profile/source "
            "URL. For a company or mixed result, this means company name plus "
            "domain/profile URL or business description."
        ),
    ),
    BooleanJudgeQuestion(
        id="exposes_useful_extra_b2b_field",
        question=(
            "Does the result expose at least one useful extra B2B field for "
            "its result type? Person examples: location, seniority, "
            "department/function, work history, tenure, education, skills, "
            "professional summary. Company examples: headquarters, "
            "headcount/company size, funding, investors, employee count, "
            "founded year, growth signal, relevant employee/profile links."
        ),
    ),
    BooleanJudgeQuestion(
        id="credited_fields_visible_in_evidence",
        question=(
            "Are the fields you would credit visibly supported by the "
            "returned evidence, rather than inferred from outside knowledge?"
        ),
    ),
    BooleanJudgeQuestion(
        id="suitable_professional_or_company_source",
        question=(
            "Is the source or page type suitable for professional or company "
            "data, such as a professional profile, company page, firmographic "
            "record, team page, or credible public web page?"
        ),
    ),
    BooleanJudgeQuestion(
        id="shows_current_professional_or_company_context",
        question=(
            "Does the result show current professional or company context, "
            "not only historical, stale, or ambiguous references?"
        ),
    ),
    BooleanJudgeQuestion(
        id="free_of_known_noise_page_types",
        question=(
            "Is the result free of known noise page types, such as job "
            "postings, career advice, resume templates, HR/recruiting "
            "software pages, staffing-agency marketing pages, generic HR "
            "blogs, or unsupported lead directories?"
        ),
    ),
    BooleanJudgeQuestion(
        id="free_of_visible_wrong_match_failures",
        question=(
            "Is the result free of visible wrong-match failures, such as "
            "wrong industry, geography, seniority, company stage, company, "
            "person, or entity type?"
        ),
    ),
)


DEFAULT_OPENAI_JUDGE_MODEL = "gpt-4o"


B2B_BOOLEAN_JUDGE_SYSTEM_PROMPT = """You judge b2b_contact_data retrieval results.

Your job is boolean classification, not numeric scoring.

Rules:
- Answer each question with exactly YES or NO.
- Do not output relevance scores, confidence percentages, or 1-10 ratings.
- Answer YES only when the returned evidence visibly supports the claim.
- If evidence is missing, ambiguous, stale, or only inferable from outside knowledge, answer NO.
- Use only the original query, candidate result, and returned evidence supplied by the caller.
- Do not require email, phone, personal address, or private contact details.
- Return one answer for every question id.
- Do not include explanations, notes, scores, or extra fields.
"""


B2B_BOOLEAN_JUDGE_USER_PROMPT = """Evaluate this b2b_contact_data candidate result.

Original query:
{original_query}

Candidate result:
{candidate_result}

Returned evidence:
{returned_evidence}

Boolean questions:
{boolean_questions}

Return JSON in this exact shape:
{{
  "answers": [
    {{
      "question_id": "is_b2b_contact_data_candidate",
      "answer": "YES"
    }}
  ]
}}
"""


def format_boolean_questions(
    questions: Tuple[BooleanJudgeQuestion, ...] = B2B_BOOLEAN_JUDGE_QUESTIONS,
) -> str:
    """Render the question list for prompt insertion."""

    return "\n".join(
        f"{index}. {question.id}: {question.question}"
        for index, question in enumerate(questions, start=1)
    )


def build_b2b_boolean_judge_user_prompt(
    original_query: str,
    candidate_result: str,
    returned_evidence: str,
) -> str:
    """Build the user prompt for one B2B candidate result."""

    return B2B_BOOLEAN_JUDGE_USER_PROMPT.format(
        original_query=original_query,
        candidate_result=candidate_result,
        returned_evidence=returned_evidence,
        boolean_questions=format_boolean_questions(),
    )


def create_openai_boolean_judge_chat_model(
    model: str = DEFAULT_OPENAI_JUDGE_MODEL,
    temperature: float = 0.0,
    **kwargs: Any,
) -> BaseChatModel:
    """Create the OpenAI chat model used for boolean judging."""

    if ChatOpenAI is None:
        raise ImportError(
            "langchain-openai is required for OpenAI judge requests. "
            "Install it and configure OPENAI_API_KEY."
        ) from _OPENAI_IMPORT_ERROR

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        **kwargs,
    )


def build_b2b_boolean_judge_prompt() -> ChatPromptTemplate:
    """Build the prompt used for structured B2B boolean judging."""

    return ChatPromptTemplate.from_messages(
        [
            ("system", B2B_BOOLEAN_JUDGE_SYSTEM_PROMPT),
            ("user", B2B_BOOLEAN_JUDGE_USER_PROMPT),
        ]
    )


def request_b2b_boolean_judge_output(
    original_query: str,
    candidate_result: Any,
    returned_evidence: Any,
    chat_model: Optional[BaseChatModel] = None,
    model: str = DEFAULT_OPENAI_JUDGE_MODEL,
) -> B2BBooleanJudgeOutputResult:
    """Call the LLM and return structured YES/NO answers for all 10 questions."""

    llm = chat_model or create_openai_boolean_judge_chat_model(model=model)
    structured_llm = llm.with_structured_output(
        B2BBooleanJudgeOutputResult, method="function_calling"
    )
    chain = build_b2b_boolean_judge_prompt() | structured_llm

    result = chain.invoke(
        {
            "original_query": original_query,
            "candidate_result": _serialize_prompt_value(candidate_result),
            "returned_evidence": _serialize_prompt_value(returned_evidence),
            "boolean_questions": format_boolean_questions(),
        }
    )

    return _validate_boolean_judge_output_result(result)


async def arequest_b2b_boolean_judge_output(
    original_query: str,
    candidate_result: Any,
    returned_evidence: Any,
    chat_model: Optional[BaseChatModel] = None,
    model: str = DEFAULT_OPENAI_JUDGE_MODEL,
) -> B2BBooleanJudgeOutputResult:
    """Async version of `request_b2b_boolean_judge_output`."""

    llm = chat_model or create_openai_boolean_judge_chat_model(model=model)
    structured_llm = llm.with_structured_output(
        B2BBooleanJudgeOutputResult, method="function_calling"
    )
    chain = build_b2b_boolean_judge_prompt() | structured_llm

    result = await chain.ainvoke(
        {
            "original_query": original_query,
            "candidate_result": _serialize_prompt_value(candidate_result),
            "returned_evidence": _serialize_prompt_value(returned_evidence),
            "boolean_questions": format_boolean_questions(),
        }
    )

    return _validate_boolean_judge_output_result(result)


def _validate_boolean_judge_output_result(
    value: Any,
) -> B2BBooleanJudgeOutputResult:
    if isinstance(value, B2BBooleanJudgeOutputResult):
        result = value
    elif hasattr(B2BBooleanJudgeOutputResult, "model_validate"):
        result = B2BBooleanJudgeOutputResult.model_validate(value)
    elif hasattr(B2BBooleanJudgeOutputResult, "parse_obj"):
        result = B2BBooleanJudgeOutputResult.parse_obj(value)
    else:
        raise TypeError("B2BBooleanJudgeOutputResult has no Pydantic validator")

    _ensure_complete_answer_set(result)
    return result


def _ensure_complete_answer_set(result: B2BBooleanJudgeOutputResult) -> None:
    expected_ids = [question.id for question in B2B_BOOLEAN_JUDGE_QUESTIONS]
    actual_ids = [answer.question_id for answer in result.answers]

    duplicate_ids = sorted(
        question_id for question_id in set(actual_ids) if actual_ids.count(question_id) > 1
    )
    missing_ids = sorted(set(expected_ids) - set(actual_ids))
    extra_ids = sorted(set(actual_ids) - set(expected_ids))

    if duplicate_ids or missing_ids or extra_ids:
        raise ValueError(
            "Boolean judge output must contain exactly one answer per question. "
            f"missing={missing_ids}, duplicate={duplicate_ids}, extra={extra_ids}"
        )


def _serialize_prompt_value(value: Any) -> str:
    if isinstance(value, str):
        return value

    if hasattr(value, "model_dump_json"):
        return value.model_dump_json(indent=2)

    if hasattr(value, "json"):
        return value.json(indent=2)

    if is_dataclass(value):
        return json.dumps(asdict(value), indent=2, default=str)

    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, indent=2, default=str)

    return str(value)
