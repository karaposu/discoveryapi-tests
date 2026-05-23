"""LLM judge for B2B contact-data SERP candidates.

Single public function:

    request_judge_verdict(original_query, link, title, snippet, chat_model=None)
        -> LLMJudgeResult

Self-contained: this file owns the question list, the system prompt, the
user prompt template, the LangChain wiring, and the conversion to the
`LLMJudgeResult` shape declared in `schemas.py`.

Input is snippet-shaped: the original query + one SERP candidate's
link + title + snippet. No page content is fetched. The 10 questions
are answered conservatively — only True when the evidence visibly
supports the claim.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field

from llm_call import call_structured
from schemas import LLMJudgeResult


DEFAULT_JUDGE_MODEL = "gpt-4o"


# ---- The 10 boolean judge questions, in order ----
#
# `boolean_answers[i]` in the returned LLMJudgeResult corresponds to
# `QUESTIONS[i]`. Order is the contract — do not reorder without
# acknowledging that downstream reports will become unaligned.

QUESTIONS: Tuple[str, ...] = (
    # 1. is_b2b_contact_data_candidate
    "Is this result a B2B contact-data candidate, not merely a generic "
    "article, product page, blog post, or topical page?",
    # 2. matches_requested_entity_type
    "Does the result match the entity type requested or implied by the "
    "query (person, company, or mixed person-company)?",
    # 3. satisfies_explicit_query_constraints
    "Does the result satisfy the query's explicit constraints — role/title, "
    "industry, geography, seniority, company type, or company stage?",
    # 4. exposes_core_identity_fields
    "Does the result expose the core identity fields required for its result "
    "type? For a person/mixed result: person name + current title or current "
    "company + profile URL. For a company/mixed result: company name + "
    "domain/profile URL or business description.",
    # 5. exposes_useful_extra_b2b_field
    "Does the result expose at least one useful extra B2B field for its "
    "result type? Person examples: location, seniority, "
    "department/function, work history, tenure, education, skills, "
    "professional summary. Company examples: headquarters, headcount, "
    "funding, investors, employee count, founded year, growth signal.",
    # 6. credited_fields_visible_in_evidence
    "Are the fields you would credit visibly supported by the returned "
    "evidence (link/title/snippet), not inferred from outside knowledge?",
    # 7. suitable_professional_or_company_source
    "Is the source or page type suitable for professional or company data "
    "(professional profile, company page, firmographic record, team page, "
    "or credible public web page)?",
    # 8. shows_current_professional_or_company_context
    "Does the result show current professional or company context, not "
    "only historical, stale, or ambiguous references?",
    # 9. free_of_known_noise_page_types
    "Is the result free of known noise page types (job postings, career "
    "advice, resume templates, HR/recruiting software pages, staffing-"
    "agency marketing pages, generic HR blogs, unsupported lead "
    "directories)?",
    # 10. free_of_visible_wrong_match_failures
    "Is the result free of visible wrong-match failures (wrong industry, "
    "geography, seniority, company stage, company, person, or entity type)?",
)


# ---- Prompts ----

_SYSTEM_PROMPT = """You judge b2b_contact_data SERP results.

You will be shown the original user query and one SERP candidate (link,
title, snippet). Answer each of the questions below with a single True
or False boolean, returned as a list IN THE SAME ORDER as the question
list.

Rules:
- True means: the evidence (link + title + snippet) visibly supports the
  claim.
- False means: the evidence is missing, ambiguous, stale, or can only be
  inferred from outside knowledge.
- Do NOT require email, phone, personal address, or other private contact
  details. Public professional / firmographic evidence is enough.
- Use only the supplied query and candidate fields. Do not browse,
  speculate, or invent.
- Return exactly as many booleans as there are questions, in the same
  order. No extra entries, no explanations, no scores.

Questions (numbered for your reference; reply with one bool per number,
in order):
{questions_block}
"""


_USER_PROMPT = """Original query:
{original_query}

Candidate result:
  link:    {link}
  title:   {title}
  snippet: {snippet}

Return a JudgeResponse whose `boolean_answers` list has one entry per
question above, in the same order."""


# ---- LLM-return shape (internal) ----

class _JudgeResponse(BaseModel):
    """The LLM's structured output. Promoted to LLMJudgeResult by the wrapper."""
    boolean_answers: List[bool] = Field(
        ...,
        description=(
            "One True/False per question, in the order given in the system prompt. "
            f"Length MUST equal {len(QUESTIONS)}."
        ),
    )


# ---- Helpers ----

def _build_questions_block() -> str:
    """Format the QUESTIONS tuple as a numbered list for prompt insertion."""
    return "\n".join(f"  {i}. {q}" for i, q in enumerate(QUESTIONS, start=1))


def _build_questions_for_record() -> str:
    """The string stored in LLMJudgeResult.original_questions for self-description.

    A numbered list of the questions, without the surrounding prompt scaffolding.
    Lets a reader of the report see which question each boolean answers.
    """
    return "\n".join(f"{i}. {q}" for i, q in enumerate(QUESTIONS, start=1))


# ---- Public function ----

def request_judge_verdict(
    original_query: str,
    link: str,
    title: Optional[str],
    snippet: Optional[str],
    chat_model: Optional[BaseChatModel] = None,
) -> LLMJudgeResult:
    """Call the LLM judge for ONE SERP candidate.

    Returns an LLMJudgeResult whose `boolean_answers` aligns positionally
    with `QUESTIONS`. Raises ValueError if the LLM returns the wrong
    number of booleans.
    """
    response = call_structured(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=_USER_PROMPT,
        output_schema=_JudgeResponse,
        template_args={
            "questions_block": _build_questions_block(),
            "original_query": original_query,
            "link": link,
            "title": title or "",
            "snippet": snippet or "",
        },
        model=DEFAULT_JUDGE_MODEL,
        chat_model=chat_model,
    )

    if len(response.boolean_answers) != len(QUESTIONS):
        raise ValueError(
            f"Judge returned {len(response.boolean_answers)} answers "
            f"but {len(QUESTIONS)} were expected."
        )

    return LLMJudgeResult(
        boolean_answers=response.boolean_answers,
        original_questions=_build_questions_for_record(),
    )
