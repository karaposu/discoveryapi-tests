"""Phase A: LLM-driven query variant generation.

Single public function:

    request_query_variants(query_spec, paradigm_seeds, variants_per_seed=…, chat_model=None)
        -> List[LLMVariantOutput]

Owns the prompts, the `VARIANTS_PER_SEED` constant, and the structured
LLM call (via `llm_call.call_structured`). The returned list is the LLM
contribution to the run — the `verbatim` baseline is added by the caller,
not produced here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from langchain_core.language_models.chat_models import BaseChatModel

from llm_call import call_structured
from schemas import B2BQuerySpec, LLMVariantOutput, LLMVariantsResponse
from utils import log_debug, log_warn


DEFAULT_MODEL = "gpt-4o"
VARIANTS_PER_SEED = 3


# ---- Prompts ----

_SYSTEM_PROMPT = """You generate semantic query variants for downstream search.

Given a query spec (JSON) and a list of paradigm seeds, produce variants
according to this rule:

  FOR EACH seed in the supplied list, produce EXACTLY {variants_per_seed}
  variants whose primary `seeds` is that seed.

Within a seed's set of variants, each one must explore a DIFFERENT
broadening approach (e.g. for `title_broadening`: one variant broadens to
abbreviations, another to functional synonyms, another to C-suite forms;
for `geography_broadening`: one uses USA/US abbreviations, another uses
regional terms, another adds state-level alternatives). Do not duplicate
a variant within a seed.

Each variant must:
- Preserve the spec's constraints (industry, geography, seniority, role/title family).
- Be shaped by the assigned seed paradigm (and may combine with others
  for the `combined_broadening` seed).
- Use Google syntax for broadenings: ("A" OR "B" OR "C") with parentheses.
- Quote multi-word phrases.
- NOT include site: operators.
- NOT include negative -keyword exclusions.
- NOT use the literal word "AND" between phrases. Google's default
  operator is already implicit AND; uppercase "AND" can be parsed
  literally and return zero results. Just separate phrases with spaces.
    RIGHT: ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" "United States"
    WRONG: ("VP Sales" OR "Head of Sales") AND "cybersecurity SaaS" AND "United States"
- List the seeds it embodies in `seeds`.
- Include a one-sentence rationale that names the specific broadening approach.

Total variants returned = {variants_per_seed} × number of seeds. The
`verbatim` baseline is NOT one of the seeds and must NOT be produced — it
is added separately by the runner.

Return a QueryVariantsResponse containing the list of variants."""


_USER_PROMPT = """Generate {variants_per_seed} variants per seed, for a total of {total_variants} variants.

Query spec:
{query_spec_json}

Paradigm seeds (produce {variants_per_seed} variants for EACH of these,
each exploring a different broadening approach):
{paradigm_seeds_list}

Return a QueryVariantsResponse."""


# ---- Public function ----

def request_query_variants(
    query_spec: B2BQuerySpec,
    paradigm_seeds: List[str],
    variants_per_seed: int = VARIANTS_PER_SEED,
    chat_model: Optional[BaseChatModel] = None,
) -> List[LLMVariantOutput]:
    """Ask the LLM for `variants_per_seed` × len(seeds) variants.

    Logs a warning (but does not raise) if the LLM returns the wrong
    count — downstream code should handle a short list.
    """
    total_expected = variants_per_seed * len(paradigm_seeds)
    log_debug(
        f"LLM call: model={DEFAULT_MODEL}, "
        f"seeds={paradigm_seeds}, variants_per_seed={variants_per_seed}, "
        f"total_expected={total_expected}"
    )

    started = datetime.now(timezone.utc)
    response = call_structured(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=_USER_PROMPT,
        output_schema=LLMVariantsResponse,
        template_args={
            "variants_per_seed": variants_per_seed,
            "total_variants": total_expected,
            "query_spec_json": query_spec.model_dump_json(indent=2),
            "paradigm_seeds_list": "\n".join(f"- {s}" for s in paradigm_seeds),
        },
        model=DEFAULT_MODEL,
        chat_model=chat_model,
    )
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    log_debug(f"LLM returned {len(response.variants)} variants in {elapsed:.1f}s")

    if len(response.variants) != total_expected:
        log_warn(
            f"LLM returned {len(response.variants)} variants but {total_expected} were requested "
            f"(seeds={paradigm_seeds}, variants_per_seed={variants_per_seed})"
        )

    return response.variants
