"""Pipeline for the B2B contact-data expansion + SERP evaluation experiment.

For each pre-built combination in `config.EXPANSION_COMBINATIONS`:

1. Ask OpenAI to render the combination into one Google search query.
2. Run Bright Data Google SERP for the rendered query.
3. Ask OpenAI to answer the 10 B2B boolean judge questions for each top-N
   candidate.

The LLM does not choose paradigms, source lanes, or parameters — those are
fixed by the combination, so downstream SERP / judge scores attribute
cleanly to one specific combination.

Configuration lives in `config.py`. Entry point lives in `runner.py`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Importing config first runs the sys.path bootstrap so the imports below
# resolve against the project root and the local Bright Data SDK source.
from previous_attempt.config import (
    AUTO_CREATE_ZONES,
    BRIGHT_DATA_GOOGLE_SERP_SOURCE,
    BRIGHTDATA_TOKEN,
    DEFAULT_EXCLUSIONS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TARGET_FIELDS,
    DEVICE,
    JUDGE_MODEL,
    JUDGE_TOP_N,
    LANGUAGE,
    LLM_MODEL,
    LOCATION,
    PROMPT_VERSION,
    QUERY,
    RESULT_COUNT,
    SERP_ZONE,
    SKIP_JUDGE,
)

# =============================================================================
# Paradigm types: the controlled vocabulary used to *define* each combination.
# =============================================================================
#
# These come from `expansion_paradigm_types.py` and are NOT the schema the LLM
# returns. They're the dial-set the runner uses to express each combination
# row in EXPANSION_COMBINATIONS below. The LLM sees these values via the
# combination's JSON dump and is told (by COMBINATION_SYSTEM_PROMPT) how to
# encode them in the Google query string.
#
# Effect on the rendered Google query:
#
#   STRONG (drop one -> noticeably different SERP results):
#     - source_lane         -> picks the site: operator (linkedin.com/in etc.)
#     - syntax_strategy     -> picks the dominant mechanic (site:, OR, -term)
#     - exclusion_strength  -> drives how many negative terms appear (1, 2, ...)
#     - industry, geography -> embedded as quoted phrases in the query
#
#   MODERATE (folded into LLM context, may or may not surface in the query):
#     - role_title_family   -> LLM may expand to title alternatives
#     - seniority_band      -> sometimes embedded as a phrase ("VP")
#     - department_or_function -> mostly context for the LLM
#
#   PURE METADATA (does NOT change the query, only the report):
#     - paradigms           -> tags WHY this combination is shaped this way
#     - entity_type         -> label only; judge infers entity from original_query
#     - discovery_flow      -> not used by single-query SERP today
#     - expected_evidence_mode -> not in the query
#     - field_intent        -> not in the query
#
# The judge prompt receives ONLY original_query, candidate_result, and
# returned_evidence — none of the combination fields are passed through.
# So any field marked "pure metadata" can be removed without affecting
# either the SERP query OR the judge's YES/NO answers.
#
# What happens if a whole enum import is removed: the combinations below
# stop compiling. So they're all required to construct the matrix as-is.
# The "drop one -> X" notes refer to *unsetting that field on a combination*
# (leaving it None), not to deleting the import.

from previous_attempt.expansion_paradigm_types import (
    # Wrapper for one combination row: label + recipe_name + paradigms + parameters.
    # The unit of the experiment. Every entry in EXPANSION_COMBINATIONS is one of these.
    ExpansionCombination,

    # Enum of 9 paradigm FAMILIES this combination embodies (e.g.
    # source_lane_targeting, noise_control, query_syntax_shaping,
    # intent_and_terminology, ...). Used to TAG each combination so the
    # report can explain *why* the query is shaped the way it is.
    # Pure metadata — never appears in the rendered query.
    ExpansionParadigm,

    # Enum: sales / engineering / marketing / security / operations / finance /
    # product / people. Sets `parameters.department_or_function`. Mostly
    # context for the LLM ("the person we want works in sales"). Weak query
    # effect. Drop it -> combinations lose a soft constraint hint.
    ExpansionParameterDepartmentOrFunction,

    # Enum: person_first / company_first / company_then_person / mixed.
    # Sets `parameters.discovery_flow`. Today this is PURE METADATA — we run
    # one SERP per combination, there's no multi-step "find companies then
    # find their VPs" flow. Useful as a label in the report. Drop it ->
    # the combination's "intended discovery path" tag disappears.
    ExpansionParameterDiscoveryFlow,

    # Enum: person_profile / company_profile / mixed_person_company.
    # Sets `parameters.entity_type`. Pure report metadata in the current
    # flow — a label so a human reading the JSON sees what each combination
    # was supposed to be hunting. Not in the query string (source_lane
    # already encodes person-vs-company). Not in the judge prompt either
    # (judge question 2 infers entity type from the original_query string
    # alone, not from this field). Drop it -> the report loses one label,
    # nothing else changes.
    ExpansionParameterEntityType,

    # Enum: snippet_only / content / structured_enrichment. Sets
    # `parameters.expected_evidence_mode`. Declares what depth of evidence
    # the combination expects to surface (just SERP snippets? full page
    # text? structured Crunchbase records?). Pure metadata for the report
    # today — the SERP retrieval is the same regardless. Drop it -> the
    # report loses one descriptive field.
    ExpansionParameterEvidenceMode,

    # Enum: light / moderate / strict. Sets `parameters.exclusion_strength`.
    # STRONG query effect — COMBINATION_SYSTEM_PROMPT uses this to decide
    # how many negative tokens to add (light -> 1, moderate -> 1-2,
    # strict -> 2). Drop it -> the LLM has no anchor for noise control and
    # may add zero or arbitrary negatives.
    ExpansionParameterExclusionStrength,

    # Enum: identity / role_fit / company_fit / firmographics / provenance.
    # Sets `parameters.field_intent`. Pure metadata — declares "this
    # combination is hunting for identity data" vs "firmographic data".
    # Useful for grouping rows in the report. No query effect today.
    ExpansionParameterFieldIntent,

    # Enum: sales_leadership / engineering_leadership / marketing_leadership /
    # security_leadership / operations_leadership. Sets
    # `parameters.role_title_family`. MODERATE query effect — the LLM may
    # expand the family into concrete titles ("VP Sales", "Head of Sales",
    # "CRO") and include them in the query. Drop it -> the LLM has less
    # context about which role family to target.
    ExpansionParameterRoleTitleFamily,

    # Enum: executive / vp / director / manager / individual_contributor.
    # Sets `parameters.seniority_band`. MODERATE query effect — the LLM
    # may embed the seniority as a phrase ("VP") or use it to filter title
    # alternatives. Drop it -> queries may match any seniority level.
    ExpansionParameterSeniorityBand,

    # Enum: linkedin_person / linkedin_company / crunchbase_person /
    # crunchbase_company / company_team_page / general_web. Sets
    # `parameters.source_lane`. STRONG query effect — the single biggest
    # dial. COMBINATION_SYSTEM_PROMPT maps this directly to a site: operator
    # (linkedin_person -> site:linkedin.com/in, etc.). Drop it -> the
    # query becomes a general web search with no source targeting.
    ExpansionParameterSourceLane,

    # The container model holding all of the above for one combination
    # (entity_type, source_lane, syntax_strategy, exclusion_strength, etc.
    # plus free-text fields like `industry` and `geography`). Used inside
    # each ExpansionCombination as `parameters=ExpansionParameters(...)`.
    ExpansionParameters,
)

# =============================================================================
# Schema types: what the LLM RETURNS, and the shape we serialize to the report.
# =============================================================================
#
# These come from `expansion_schemas.py`. Different concern from the paradigm
# types above:
#   - paradigm types = our INPUT vocabulary (what we tell the LLM the
#     combination IS),
#   - schema types = the OUTPUT shape (what the LLM returns + what ends up
#     in the JSON report).

from previous_attempt.expansion_schemas import (
    # The LLM's return type for one combination call. Deliberately small:
    # `query` plus a short trace (preserved/broadened constraints, rationale,
    # risk_notes). The LLM does NOT echo entity_type, source_lane, etc. —
    # Python fills those in from the combination, eliminating hallucination.
    CombinationExpansionDraft,

    # Runner-owned config metadata recorded in the report (model name,
    # prompt_version, allowed lanes/fields/exclusions, etc.). Not sent to
    # the LLM in the current flow — purely for the report's self-description.
    ExpansionExperimentConfig,

    # Same string values as ExpansionParameterDiscoveryFlow above, but a
    # DIFFERENT enum class. Required because ExpansionOutputItem uses this
    # version of the enum. We convert between them by `.value` in
    # build_expansion_output_item().
    ExpansionOutputDiscoveryFlow,

    # Same string values as ExpansionParameterEntityType. Used in
    # ExpansionOutputItem.entity_type. Conversion via `.value`.
    ExpansionOutputEntityType,

    # Same string values as ExpansionParameterEvidenceMode. Used in
    # ExpansionOutputItem.expected_evidence_mode. Conversion via `.value`.
    ExpansionOutputEvidenceMode,

    # The final per-expansion record that goes into the report's
    # `expansion_result.expansions[]` and into each `records[].expansion`.
    # Built by build_expansion_output_item() from (combination + LLM draft).
    ExpansionOutputItem,

    # Schema-side mirror of ExpansionParadigm. Used in
    # ExpansionOutputTrace.paradigms. Conversion via `.value`.
    ExpansionOutputParadigm,

    # Wraps a list of ExpansionOutputItem plus run metadata (result_id,
    # model, prompt_version, original_query). The top-level expansion
    # report payload.
    ExpansionOutputResult,

    # Same string values as ExpansionParameterSourceLane. Used in
    # ExpansionOutputItem.source_lane. Conversion via `.value`.
    ExpansionOutputSourceLane,

    # The trace block inside each ExpansionOutputItem: recipe_name,
    # paradigms, preserved/broadened constraints, rationale.
    ExpansionOutputTrace,

    # The schema-side syntax strategy enum used in ExpansionOutputItem.
    # NAME CLASH: ExpansionQuerySyntaxStrategy ALSO exists in
    # expansion_paradigm_types with the same string values but as a
    # different class. The paradigm-types version is aliased below as
    # `_ParadigmSyntaxStrategy` so both can coexist in this module.
    ExpansionQuerySyntaxStrategy,
)

# Alias of the paradigm-types syntax strategy enum (different class, same
# string values as the schemas version above). Used when DEFINING
# combinations; the schemas version is used when CONSTRUCTING
# ExpansionOutputItem instances. The two get reconciled by `.value` lookup
# inside build_expansion_output_item().
from previous_attempt.expansion_paradigm_types import (
    ExpansionQuerySyntaxStrategy as _ParadigmSyntaxStrategy,
)


# ---- Expansion combinations (the experiment being run) ----
#
# Each combination is one fully-specified paradigm + parameters bundle. The
# runner makes one LLM call per combination, and the LLM is asked only to
# render a concrete query string + trace. Paradigms, source lanes, and
# parameter values are fixed here — not chosen by the LLM — so downstream
# SERP / judge scores attribute cleanly to a specific combination.

_PERSON_TARGET_FIELDS = [
    "person_name",
    "current_title",
    "current_company",
    "profile_or_source_url",
    "location",
    "seniority",
    "department_or_function",
]

_COMPANY_TARGET_FIELDS = [
    "company_name",
    "company_domain_or_profile_url",
    "industry_or_description",
    "headquarters_or_location",
    "headcount_or_company_size",
    "funding",
    "founded_year",
]


# =============================================================================
# The ablation matrix. Each row is one combination = one LLM call = one SERP
# query = one row in the report's `combinations[]`. The label is what shows
# up in record `metadata.combination_label` so you can slice the report.
#
# Caveat: these 5 rows are "maximalist bundles" — every row enables several
# paradigms at once. That makes per-factor attribution impossible (you can't
# tell whether site: helped or whether negatives helped from this matrix
# alone). See `devdocs/scoped/1/how_should_be.md` for the proper factorial
# ablation design we should move toward (baseline + isolated factors + pairs).
# =============================================================================

EXPANSION_COMBINATIONS: List[ExpansionCombination] = [
    # -------------------------------------------------------------------------
    # [1] linkedin_person_strict
    # -------------------------------------------------------------------------
    # Hypothesis: the most aggressive "find the VP Sales person directly"
    # configuration. LinkedIn-only via site:, strict negatives to suppress
    # job boards and recruiting software. Should give the highest PRECISION
    # of person profiles but may miss titles outside the sales_leadership
    # family (e.g. "Chief Revenue Officer" if the LLM doesn't expand titles).
    #
    # Expected query shape:
    #   site:linkedin.com/in "VP Sales" "cybersecurity SaaS" "United States" -jobs -hiring
    #
    # Watch for: missing CRO/Head of Revenue results; over-pruned SERPs;
    # very few candidates when LinkedIn rate-limits the site: prefix.
    ExpansionCombination(
        label="linkedin_person_strict",
        recipe_name="Source-Aware Person-First",
        paradigms=[
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.entity_targeting,
            ExpansionParadigm.discovery_flow,
            ExpansionParadigm.noise_control,
            ExpansionParadigm.query_syntax_shaping,
        ],
        parameters=ExpansionParameters(
            entity_type=ExpansionParameterEntityType.person_profile,
            discovery_flow=ExpansionParameterDiscoveryFlow.person_first,
            source_lane=ExpansionParameterSourceLane.linkedin_person,
            role_title_family=ExpansionParameterRoleTitleFamily.sales_leadership,
            seniority_band=ExpansionParameterSeniorityBand.vp,
            department_or_function=ExpansionParameterDepartmentOrFunction.sales,
            industry="cybersecurity SaaS",
            geography="United States",
            target_fields=_PERSON_TARGET_FIELDS,
            exclusions=DEFAULT_EXCLUSIONS,
            expected_evidence_mode=ExpansionParameterEvidenceMode.snippet_only,
            syntax_strategy=_ParadigmSyntaxStrategy.site_operator,
            field_intent=ExpansionParameterFieldIntent.identity,
            exclusion_strength=ExpansionParameterExclusionStrength.strict,
        ),
    ),
    # -------------------------------------------------------------------------
    # [2] linkedin_person_boolean_or
    # -------------------------------------------------------------------------
    # Hypothesis: same target (LinkedIn person profiles) but trades PRECISION
    # for RECALL by broadening titles via OR. Should catch more title
    # variants ("VP Sales" OR "Head of Sales" OR "Director of Sales"...) at
    # the cost of more noise. Moderate exclusions because if we're broader
    # on title we want to be less aggressive on negatives — otherwise we
    # wipe out the broadening's benefit.
    #
    # Expected query shape:
    #   ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" "United States" -jobs
    #
    # Compare to [1]: if [2] beats [1] on yes_count, title broadening was
    # the bottleneck. If [1] beats [2], strict negatives matter more than
    # title coverage.
    ExpansionCombination(
        label="linkedin_person_boolean_or",
        recipe_name="Broad Semantic Recall",
        paradigms=[
            ExpansionParadigm.intent_and_terminology,
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.query_syntax_shaping,
            ExpansionParadigm.noise_control,
        ],
        parameters=ExpansionParameters(
            entity_type=ExpansionParameterEntityType.person_profile,
            discovery_flow=ExpansionParameterDiscoveryFlow.person_first,
            source_lane=ExpansionParameterSourceLane.linkedin_person,
            role_title_family=ExpansionParameterRoleTitleFamily.sales_leadership,
            seniority_band=ExpansionParameterSeniorityBand.vp,
            department_or_function=ExpansionParameterDepartmentOrFunction.sales,
            industry="cybersecurity SaaS",
            geography="United States",
            target_fields=_PERSON_TARGET_FIELDS,
            exclusions=DEFAULT_EXCLUSIONS,
            expected_evidence_mode=ExpansionParameterEvidenceMode.snippet_only,
            syntax_strategy=_ParadigmSyntaxStrategy.boolean_or,
            field_intent=ExpansionParameterFieldIntent.identity,
            exclusion_strength=ExpansionParameterExclusionStrength.moderate,
        ),
    ),
    # -------------------------------------------------------------------------
    # [3] linkedin_company
    # -------------------------------------------------------------------------
    # Hypothesis: company-first discovery via LinkedIn company pages. Don't
    # try to find the VP directly; find the cybersecurity SaaS startups
    # first, then (downstream, in a future pipeline step) look inside them
    # for sales leaders. Target fields shift to firmographic shape
    # (headcount, funding, founded_year, ...).
    #
    # Expected query shape:
    #   site:linkedin.com/company "cybersecurity SaaS" startup "United States"
    #
    # Watch for: irrelevant company pages (security service providers vs
    # SaaS vendors); the judge's matches_requested_entity_type should flip
    # to "company_profile" expectations for this row.
    ExpansionCombination(
        label="linkedin_company",
        recipe_name="Source-Aware Company-First",
        paradigms=[
            ExpansionParadigm.entity_targeting,
            ExpansionParadigm.discovery_flow,
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.field_and_evidence_targeting,
        ],
        parameters=ExpansionParameters(
            entity_type=ExpansionParameterEntityType.company_profile,
            discovery_flow=ExpansionParameterDiscoveryFlow.company_first,
            source_lane=ExpansionParameterSourceLane.linkedin_company,
            industry="cybersecurity SaaS",
            geography="United States",
            company_type="startup",
            target_fields=_COMPANY_TARGET_FIELDS,
            exclusions=DEFAULT_EXCLUSIONS,
            expected_evidence_mode=ExpansionParameterEvidenceMode.snippet_only,
            syntax_strategy=_ParadigmSyntaxStrategy.site_operator,
            field_intent=ExpansionParameterFieldIntent.firmographics,
            exclusion_strength=ExpansionParameterExclusionStrength.moderate,
        ),
    ),
    # -------------------------------------------------------------------------
    # [4] crunchbase_company
    # -------------------------------------------------------------------------
    # Hypothesis: Crunchbase has richer STRUCTURED firmographic data
    # (funding rounds, employee counts, investors) than LinkedIn snippets.
    # Light exclusions because Crunchbase doesn't have job-board noise to
    # begin with — strict negatives would just shrink the SERP unnecessarily.
    # expected_evidence_mode=structured_enrichment flags this combination
    # as the one most likely to yield API-enrichable records downstream.
    #
    # Expected query shape:
    #   site:crunchbase.com/organization "cybersecurity SaaS" startup
    #
    # Compare to [3]: if Crunchbase wins on firmographic fields visible in
    # snippets (funding, headcount), source matters more than syntax. If
    # LinkedIn [3] wins, snippet quality outweighs source choice.
    ExpansionCombination(
        label="crunchbase_company",
        recipe_name="Field-Intent Enriched-Data",
        paradigms=[
            ExpansionParadigm.field_and_evidence_targeting,
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.tool_and_evidence_mode_targeting,
        ],
        parameters=ExpansionParameters(
            entity_type=ExpansionParameterEntityType.company_profile,
            discovery_flow=ExpansionParameterDiscoveryFlow.company_first,
            source_lane=ExpansionParameterSourceLane.crunchbase_company,
            industry="cybersecurity SaaS",
            geography="United States",
            company_type="startup",
            target_fields=_COMPANY_TARGET_FIELDS,
            exclusions=DEFAULT_EXCLUSIONS,
            expected_evidence_mode=ExpansionParameterEvidenceMode.structured_enrichment,
            syntax_strategy=_ParadigmSyntaxStrategy.site_operator,
            field_intent=ExpansionParameterFieldIntent.firmographics,
            exclusion_strength=ExpansionParameterExclusionStrength.light,
        ),
    ),
    # -------------------------------------------------------------------------
    # [5] general_web_exclusion_heavy
    # -------------------------------------------------------------------------
    # Hypothesis: no site: operator at all — open Google search with strong
    # negative filtering as the only noise control. Tests whether you can
    # match LinkedIn-style precision without restricting to LinkedIn. mixed
    # entity_type means the judge accepts either person OR company results.
    # This is the "control" for source_lane: if [1]/[3]/[4] all beat [5],
    # source restriction is the lever, not query shaping.
    #
    # Expected query shape:
    #   "VP Sales" "cybersecurity SaaS" "United States" -jobs -hiring
    #
    # Watch for: lots of company team pages, blog posts, news articles. If
    # judge's free_of_known_noise_page_types stays high here, the negatives
    # alone are doing the work and the site: operator may be redundant.
    ExpansionCombination(
        label="general_web_exclusion_heavy",
        recipe_name="Exclusion-Heavy Precision",
        paradigms=[
            ExpansionParadigm.noise_control,
            ExpansionParadigm.query_syntax_shaping,
            ExpansionParadigm.constraint_handling,
        ],
        parameters=ExpansionParameters(
            entity_type=ExpansionParameterEntityType.mixed_person_company,
            discovery_flow=ExpansionParameterDiscoveryFlow.mixed,
            source_lane=ExpansionParameterSourceLane.general_web,
            role_title_family=ExpansionParameterRoleTitleFamily.sales_leadership,
            seniority_band=ExpansionParameterSeniorityBand.vp,
            industry="cybersecurity SaaS",
            geography="United States",
            target_fields=_PERSON_TARGET_FIELDS + _COMPANY_TARGET_FIELDS,
            exclusions=DEFAULT_EXCLUSIONS,
            expected_evidence_mode=ExpansionParameterEvidenceMode.snippet_only,
            syntax_strategy=_ParadigmSyntaxStrategy.negative_terms,
            field_intent=ExpansionParameterFieldIntent.identity,
            exclusion_strength=ExpansionParameterExclusionStrength.strict,
        ),
    ),
]


def run() -> Dict[str, Any]:
    started_at = datetime.now(timezone.utc)
    run_id = started_at.strftime("b2b_%Y%m%d_%H%M%S")

    config = build_expansion_config()
    total_combos = len(EXPANSION_COMBINATIONS)

    _log(f"run_id={run_id}  query={QUERY!r}")
    _log(
        f"combinations={total_combos}  llm={LLM_MODEL}  "
        f"judge={'SKIP' if SKIP_JUDGE else JUDGE_MODEL}  "
        f"serp_count={RESULT_COUNT}  judge_top_n={JUDGE_TOP_N}"
    )

    report: Dict[str, Any] = {
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "query": QUERY,
        "retrieval_method": BRIGHT_DATA_GOOGLE_SERP_SOURCE,
        "skip_judge": SKIP_JUDGE,
        "experiment_config": to_serializable(config),
        "combinations": [to_serializable(c) for c in EXPANSION_COMBINATIONS],
        "expansion_result": None,
        "records": [],
    }

    from previous_attempt.llm_request_logic import request_expansion_for_combination
    from previous_attempt.retrieval import BrightDataGoogleSERPRetrievalClient

    _log("expanding combinations...")
    expansion_items: List[ExpansionOutputItem] = []
    for index, combination in enumerate(EXPANSION_COMBINATIONS, start=1):
        _log(f"  [{index}/{total_combos}] {combination.label} -- calling LLM")
        t0 = datetime.now(timezone.utc)
        draft = request_expansion_for_combination(
            original_query=QUERY,
            combination=combination,
            model=LLM_MODEL,
        )
        dt = (datetime.now(timezone.utc) - t0).total_seconds()
        _log(f"  [{index}/{total_combos}] {combination.label} -- {dt:.1f}s  query={draft.query!r}")
        expansion_items.append(
            build_expansion_output_item(combination, draft, index)
        )

    expansion_result = ExpansionOutputResult(
        result_id=f"combo_{run_id}",
        model=LLM_MODEL,
        prompt_version=PROMPT_VERSION,
        original_query=QUERY,
        expansions=expansion_items,
        generation_notes="One LLM call per pre-built combination in EXPANSION_COMBINATIONS.",
    )
    report["expansion_result"] = to_serializable(expansion_result)

    retrieval_client = BrightDataGoogleSERPRetrievalClient(
        token=BRIGHTDATA_TOKEN,
        serp_zone=SERP_ZONE,
        auto_create_zones=AUTO_CREATE_ZONES,
        default_location=LOCATION,
        default_language=LANGUAGE,
        default_device=DEVICE,
    )

    _log("retrieval + judging...")
    report["records"] = run_retrieval_and_judging(
        expansion_result=expansion_result,
        retrieval_client=retrieval_client,
    )
    report["completed_at"] = datetime.now(timezone.utc).isoformat()

    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
    _log(f"done in {elapsed:.1f}s  records={len(report['records'])}")
    return report


def _log(message: str) -> None:
    """Single-line progress print, flushed so it shows up live."""
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def build_expansion_config() -> ExpansionExperimentConfig:
    return ExpansionExperimentConfig(
        model=LLM_MODEL,
        prompt_version=PROMPT_VERSION,
        num_expansions=len(EXPANSION_COMBINATIONS),
        allowed_entity_types=[
            ExpansionOutputEntityType.person_profile,
            ExpansionOutputEntityType.company_profile,
            ExpansionOutputEntityType.mixed_person_company,
        ],
        allowed_source_lanes=[
            ExpansionOutputSourceLane.linkedin_person,
            ExpansionOutputSourceLane.linkedin_company,
            ExpansionOutputSourceLane.crunchbase_person,
            ExpansionOutputSourceLane.crunchbase_company,
            ExpansionOutputSourceLane.company_team_page,
            ExpansionOutputSourceLane.general_web,
        ],
        allowed_evidence_modes=[
            ExpansionOutputEvidenceMode.snippet_only,
            ExpansionOutputEvidenceMode.content,
            ExpansionOutputEvidenceMode.structured_enrichment,
        ],
        allowed_target_fields=DEFAULT_TARGET_FIELDS,
        allowed_exclusions=DEFAULT_EXCLUSIONS,
        fixed_retrieval_method=BRIGHT_DATA_GOOGLE_SERP_SOURCE,
        fixed_result_count=RESULT_COUNT,
        locale=LOCATION,
    )


def build_expansion_output_item(
    combination: ExpansionCombination,
    draft: CombinationExpansionDraft,
    index: int,
) -> ExpansionOutputItem:
    """Wrap an LLM draft + its combination into a full `ExpansionOutputItem`.

    The combination already fixes entity_type, source_lane, paradigms, etc.
    Those don't need to come back from the LLM; we just translate the
    paradigm-types enums into their expansion-schemas counterparts.
    """

    params = combination.parameters

    return ExpansionOutputItem(
        expansion_id=f"exp_{index:02d}_{combination.label}",
        entity_type=ExpansionOutputEntityType(params.entity_type.value),
        source_lane=ExpansionOutputSourceLane(params.source_lane.value),
        query=draft.query,
        target_fields=list(params.target_fields),
        exclusions=list(params.exclusions),
        expansion_trace=ExpansionOutputTrace(
            recipe_name=combination.recipe_name,
            paradigms=[
                ExpansionOutputParadigm(p.value) for p in combination.paradigms
            ],
            preserved_constraints=list(draft.preserved_constraints),
            broadened_constraints=list(draft.broadened_constraints),
            broadening_axis=draft.broadening_axis,
            rationale=draft.rationale,
        ),
        expected_evidence_mode=ExpansionOutputEvidenceMode(
            params.expected_evidence_mode.value
        ),
        risk_notes=list(draft.risk_notes),
        discovery_flow=ExpansionOutputDiscoveryFlow(params.discovery_flow.value),
        syntax_strategy=(
            ExpansionQuerySyntaxStrategy(params.syntax_strategy.value)
            if params.syntax_strategy is not None
            else None
        ),
        metadata={"combination_label": combination.label},
    )


def run_retrieval_and_judging(
    expansion_result: ExpansionOutputResult,
    retrieval_client: Any,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    judge_request = None

    if not SKIP_JUDGE:
        from previous_attempt.evaluation.b2b.boolean_questions import request_b2b_boolean_judge_output

        judge_request = request_b2b_boolean_judge_output

    total_exp = len(expansion_result.expansions)
    for ix, expansion in enumerate(expansion_result.expansions, start=1):
        label = (expansion.metadata or {}).get(
            "combination_label", expansion.expansion_id
        )

        _log(f"  [{ix}/{total_exp}] {label} -- SERP")
        t_serp = datetime.now(timezone.utc)
        candidates = retrieval_client.search_sync(
            query=expansion.query,
            result_count=RESULT_COUNT,
            location=LOCATION,
            language=LANGUAGE,
            device=DEVICE,
            zone=SERP_ZONE,
        )
        dt_serp = (datetime.now(timezone.utc) - t_serp).total_seconds()
        _log(
            f"  [{ix}/{total_exp}] {label} -- {len(candidates)} candidates "
            f"({dt_serp:.1f}s)"
        )

        topn = candidates[:JUDGE_TOP_N]
        if judge_request is not None and topn:
            _log(f"  [{ix}/{total_exp}] {label} -- judging top {len(topn)}")

        for jx, candidate in enumerate(topn, start=1):
            judge_result: Optional[Any] = None

            if judge_request is not None:
                judge_result = judge_request(
                    original_query=QUERY,
                    candidate_result=candidate_prompt_payload(candidate),
                    returned_evidence=candidate_evidence_payload(candidate),
                    model=JUDGE_MODEL,
                )
                ys = sum(1 for a in judge_result.answers if a.answer == "YES")
                url_preview = (candidate.url or "")[:60]
                _log(
                    f"    [{jx}/{len(topn)}] yes={ys:2d}/10  {url_preview}"
                )

            records.append(
                {
                    "prompt_version": expansion_result.prompt_version,
                    "original_query": QUERY,
                    "expansion": to_serializable(expansion),
                    "retrieved_candidate": to_serializable(candidate),
                    "judge_result": (
                        to_serializable(judge_result) if judge_result else None
                    ),
                    "boolean_summary": (
                        summarize_boolean_answers(judge_result)
                        if judge_result
                        else None
                    ),
                }
            )

    return records


def candidate_prompt_payload(candidate: Any) -> Dict[str, Any]:
    return {
        "rank": candidate.rank,
        "source_name": candidate.source_name,
        "url": candidate.url,
        "title": candidate.title,
        "snippet": candidate.snippet,
    }


def candidate_evidence_payload(candidate: Any) -> Dict[str, Any]:
    return {
        "url": candidate.url,
        "title": candidate.title,
        "snippet": candidate.snippet,
        "content": candidate.content,
        "structured_fields": candidate.structured_fields,
    }


def summarize_boolean_answers(judge_result: Any) -> Dict[str, Any]:
    yes_ids = [
        answer.question_id for answer in judge_result.answers if answer.answer == "YES"
    ]
    no_ids = [
        answer.question_id for answer in judge_result.answers if answer.answer == "NO"
    ]

    return {
        "yes_count": len(yes_ids),
        "no_count": len(no_ids),
        "yes_question_ids": yes_ids,
        "no_question_ids": no_ids,
    }


def save_report(report: Dict[str, Any]) -> Path:
    output_path = DEFAULT_OUTPUT_DIR / f"{report['run_id']}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return output_path


def to_serializable(value: Any) -> Any:
    if value is None:
        return None

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    if hasattr(value, "dict"):
        return value.dict()

    if is_dataclass(value):
        return asdict(value)

    if isinstance(value, dict):
        return {key: to_serializable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]

    return value
