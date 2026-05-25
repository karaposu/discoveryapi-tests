"""Pydantic types for `b2b_contact_data` expansion paradigms.

These types describe how the expansion LLM should produce structured,
composable search expansions instead of plain strings or random prompt
rewrites.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


B2BContactDataCategoryName = Literal["b2b_contact_data"]


class ExpansionParadigm(str, Enum):
    """Reusable query-transformation dimensions.

    A paradigm is not a whole prompt variant. It is one way a prompt can
    transform or target the original query. Recipes combine several paradigms.
    """

    # Changes role, industry, or concept wording while preserving the user's
    # intent.
    #
    # Examples:
    # - "Head of Sales" -> "VP Sales"
    # - "sales leader" -> "Chief Revenue Officer"
    # - "cybersecurity SaaS" -> "security software"
    intent_and_terminology = "intent_and_terminology"

    # Chooses what kind of result the expansion is trying to find.
    #
    # Examples:
    # - Find person profiles for "heads of sales"
    # - Find company profiles for "cybersecurity SaaS companies"
    entity_targeting = "entity_targeting"

    # Chooses the discovery path.
    #
    # Examples:
    # - Person-first: search directly for "VP Sales cybersecurity SaaS"
    # - Company-first: find cybersecurity SaaS companies before looking for
    #   sales leaders inside them
    discovery_flow = "discovery_flow"

    # Targets a source family or source shape.
    #
    # Examples:
    # - site:linkedin.com/in "VP Sales" "cybersecurity SaaS"
    # - site:linkedin.com/company "cybersecurity SaaS"
    # - site:crunchbase.com/organization cybersecurity SaaS
    source_lane_targeting = "source_lane_targeting"

    # Controls which original constraints are preserved and which are broadened.
    #
    # Examples:
    # - Preserve geography: "United States"
    # - Broaden title: "Head of Sales" -> "VP Sales" OR "Sales Director"
    # - Broaden source: LinkedIn-only -> LinkedIn plus company team pages
    constraint_handling = "constraint_handling"

    # Biases the expansion toward sources likely to expose fields from the
    # B2B contact-data contract.
    #
    # Examples:
    # - Add terms likely to surface person name, current title, current company
    # - Search company profile sources likely to expose industry, funding, size
    field_and_evidence_targeting = "field_and_evidence_targeting"

    # Avoids known bad result types.
    #
    # Examples:
    # - Avoid job postings, career advice, resume templates
    # - Avoid HR software pages and generic HR blogs
    noise_control = "noise_control"

    # Controls how the search query is expressed.
    #
    # Examples:
    # - Use quoted phrases: "Head of Sales"
    # - Use site operators: site:linkedin.com/in
    # - Use exclusions: -jobs -hiring -resume
    query_syntax_shaping = "query_syntax_shaping"

    # Shapes the expansion for the kind of downstream evidence expected.
    #
    # Examples:
    # - SERP-oriented URL discovery
    # - WSAPI route hint for LinkedIn or Crunchbase enrichment
    # - Dataset/entity lookup for company records
    tool_and_evidence_mode_targeting = "tool_and_evidence_mode_targeting"


class ExpansionParameterEntityType(str, Enum):
    """The target result type for a generated expansion."""

    person_profile = "person_profile"
    company_profile = "company_profile"
    mixed_person_company = "mixed_person_company"


class ExpansionParameterDiscoveryFlow(str, Enum):
    """The intended discovery path."""

    person_first = "person_first"
    company_first = "company_first"
    company_then_person = "company_then_person"
    mixed = "mixed"


class ExpansionParameterSourceLane(str, Enum):
    """The source family a query is targeting."""

    linkedin_person = "linkedin_person"
    linkedin_company = "linkedin_company"
    crunchbase_person = "crunchbase_person"
    crunchbase_company = "crunchbase_company"
    company_team_page = "company_team_page"
    general_web = "general_web"


class ExpansionParameterRoleTitleFamily(str, Enum):
    """Controlled role/title families for title expansion."""

    sales_leadership = "sales_leadership"
    engineering_leadership = "engineering_leadership"
    marketing_leadership = "marketing_leadership"
    security_leadership = "security_leadership"
    operations_leadership = "operations_leadership"


class ExpansionParameterSeniorityBand(str, Enum):
    """Seniority level targeted by the expansion."""

    executive = "executive"
    vp = "vp"
    director = "director"
    manager = "manager"
    individual_contributor = "individual_contributor"


class ExpansionParameterDepartmentOrFunction(str, Enum):
    """Business function targeted by the expansion."""

    sales = "sales"
    security = "security"
    engineering = "engineering"
    marketing = "marketing"
    operations = "operations"
    finance = "finance"
    product = "product"
    people = "people"


class ExpansionParameterBroadeningAxis(str, Enum):
    """Which constraint was broadened, if any."""

    none = "none"
    title = "title"
    industry = "industry"
    geography = "geography"
    source = "source"
    company_type = "company_type"
    seniority = "seniority"


class ExpansionParameterConstraintStrictness(str, Enum):
    """How strictly the expansion preserves original constraints."""

    strict = "strict"
    moderate = "moderate"
    broad = "broad"


class ExpansionParameterEvidenceMode(str, Enum):
    """The evidence mode the query is expected to surface."""

    snippet_only = "snippet_only"
    content = "content"
    structured_enrichment = "structured_enrichment"


class ExpansionQuerySyntaxStrategy(str, Enum):
    """How the generated search query is written."""

    natural_language = "natural_language"
    quoted_phrase = "quoted_phrase"
    site_operator = "site_operator"
    boolean_or = "boolean_or"
    negative_terms = "negative_terms"
    exact_title = "exact_title"


class ExpansionParameterExclusionStrength(str, Enum):
    """How aggressively an expansion tries to avoid noisy results."""

    light = "light"
    moderate = "moderate"
    strict = "strict"


class ExpansionParameterFieldIntent(str, Enum):
    """Why the expansion targets a set of fields."""

    identity = "identity"
    role_fit = "role_fit"
    company_fit = "company_fit"
    firmographics = "firmographics"
    provenance = "provenance"


class ExpansionParameterConstraintChange(BaseModel):
    """A preserved or broadened query constraint."""

    name: str
    original_value: str
    expanded_value: Optional[str] = None
    note: Optional[str] = None


class ExpansionParameterConstraints(BaseModel):
    """Constraints preserved or broadened by one generated expansion."""

    preserved: List[ExpansionParameterConstraintChange] = Field(default_factory=list)
    broadened: List[ExpansionParameterConstraintChange] = Field(default_factory=list)
    broadening_axis: ExpansionParameterBroadeningAxis = ExpansionParameterBroadeningAxis.none
    strictness: ExpansionParameterConstraintStrictness = ExpansionParameterConstraintStrictness.moderate


class ExpansionParameters(BaseModel):
    """Controlled parameter values used to generate an expansion."""

    entity_type: ExpansionParameterEntityType
    discovery_flow: ExpansionParameterDiscoveryFlow
    source_lane: ExpansionParameterSourceLane
    role_title_family: Optional[ExpansionParameterRoleTitleFamily] = None
    seniority_band: Optional[ExpansionParameterSeniorityBand] = None
    department_or_function: Optional[ExpansionParameterDepartmentOrFunction] = None
    industry: Optional[str] = None
    geography: Optional[str] = None
    company_type: Optional[str] = None
    company_size_or_stage: Optional[str] = None
    target_fields: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)
    expected_evidence_mode: ExpansionParameterEvidenceMode = ExpansionParameterEvidenceMode.snippet_only
    syntax_strategy: Optional[ExpansionQuerySyntaxStrategy] = None
    field_intent: Optional[ExpansionParameterFieldIntent] = None
    exclusion_strength: Optional[ExpansionParameterExclusionStrength] = None


class ExpansionCombination(BaseModel):
    """A pre-built paradigm + parameters bundle that drives one LLM call.

    The runner enumerates a list of these. For each combination, the LLM is
    asked only to render a single concrete query string plus a small trace.
    The LLM does not pick paradigms, source lanes, or parameters — those are
    fixed in advance, which gives clean A/B attribution to downstream SERP
    quality.
    """

    label: str
    recipe_name: str
    paradigms: List[ExpansionParadigm]
    parameters: ExpansionParameters


class ExpansionParadigmRecipe(BaseModel):
    """A named combination of paradigms and parameters."""

    recipe_name: str
    description: str
    paradigms: List[ExpansionParadigm]
    default_parameters: Dict[str, str] = Field(default_factory=dict)
    useful_when: List[str] = Field(default_factory=list)
    main_risks: List[str] = Field(default_factory=list)


class ExpansionParadigmStructuredOutput(BaseModel):
    """The compact object the LLM should return for one generated expansion."""

    expansion_id: str
    paradigms: List[ExpansionParadigm]
    entity_type: ExpansionParameterEntityType
    discovery_flow: ExpansionParameterDiscoveryFlow
    source_lane: ExpansionParameterSourceLane
    query: str
    constraints: ExpansionParameterConstraints
    target_fields: List[str]
    exclusions: List[str] = Field(default_factory=list)
    expected_evidence_mode: ExpansionParameterEvidenceMode
    risk_notes: List[str] = Field(default_factory=list)
    broadening_axis: Optional[ExpansionParameterBroadeningAxis] = None
    syntax_strategy: Optional[ExpansionQuerySyntaxStrategy] = None
    enrichment_hint: Optional[str] = None
    diagnostic_purpose: Optional[str] = None


class ExpansionParadigmMap(BaseModel):
    """Complete paradigm map for `b2b_contact_data` expansion generation."""

    category: B2BContactDataCategoryName = "b2b_contact_data"
    paradigm_groups: List[ExpansionParadigm] = Field(
        default_factory=lambda: list(ExpansionParadigm)
    )
    recipes: List[ExpansionParadigmRecipe] = Field(default_factory=list)


B2B_CONTACT_DATA_EXPANSION_RECIPES: List[ExpansionParadigmRecipe] = [
    ExpansionParadigmRecipe(
        recipe_name="Broad Semantic Recall",
        description="Expands terminology to find more potentially relevant results.",
        paradigms=[
            ExpansionParadigm.intent_and_terminology,
            ExpansionParadigm.constraint_handling,
            ExpansionParadigm.noise_control,
        ],
        useful_when=[
            "role/title language varies",
            "industry wording varies",
            "recall is too low",
        ],
        main_risks=["more noisy results", "semantic drift from the original query"],
    ),
    ExpansionParadigmRecipe(
        recipe_name="Strict Constraint-Preserving",
        description="Keeps the original query constraints as intact as possible.",
        paradigms=[
            ExpansionParadigm.constraint_handling,
            ExpansionParadigm.query_syntax_shaping,
            ExpansionParadigm.noise_control,
        ],
        useful_when=[
            "broad expansions drift too much",
            "the original query has strong filters",
        ],
        main_risks=["misses useful profiles with different wording"],
    ),
    ExpansionParadigmRecipe(
        recipe_name="Source-Aware Person-First",
        description="Finds individual professional profiles directly.",
        paradigms=[
            ExpansionParadigm.entity_targeting,
            ExpansionParadigm.discovery_flow,
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.intent_and_terminology,
            ExpansionParadigm.noise_control,
        ],
        useful_when=[
            "the target role is clear",
            "LinkedIn or Crunchbase person results are expected",
        ],
        main_risks=[
            "returns people outside the requested company type",
            "returns people outside the requested geography",
        ],
    ),
    ExpansionParadigmRecipe(
        recipe_name="Source-Aware Company-First",
        description="Finds target companies before looking for people.",
        paradigms=[
            ExpansionParadigm.entity_targeting,
            ExpansionParadigm.discovery_flow,
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.field_and_evidence_targeting,
        ],
        useful_when=[
            "direct person search is sparse",
            "company fit matters strongly",
        ],
        main_risks=["finds companies but not contacts"],
    ),
    ExpansionParadigmRecipe(
        recipe_name="Field-Intent Enriched-Data",
        description="Targets sources likely to expose useful B2B fields.",
        paradigms=[
            ExpansionParadigm.field_and_evidence_targeting,
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.tool_and_evidence_mode_targeting,
        ],
        useful_when=[
            "later enrichment will run",
            "field coverage matters",
        ],
        main_risks=["query may become unnatural or too constrained"],
    ),
    ExpansionParadigmRecipe(
        recipe_name="Exclusion-Heavy Precision",
        description="Reduces predictable B2B noise.",
        paradigms=[
            ExpansionParadigm.noise_control,
            ExpansionParadigm.query_syntax_shaping,
            ExpansionParadigm.constraint_handling,
        ],
        useful_when=[
            "results contain job postings",
            "results contain HR blogs, career advice, or software pages",
        ],
        main_risks=["negative terms may suppress useful results"],
    ),
    ExpansionParadigmRecipe(
        recipe_name="Company-First Then Person-Followup",
        description=(
            "Uses company discovery first, then searches for target roles "
            "inside those companies."
        ),
        paradigms=[
            ExpansionParadigm.discovery_flow,
            ExpansionParadigm.entity_targeting,
            ExpansionParadigm.field_and_evidence_targeting,
            ExpansionParadigm.source_lane_targeting,
        ],
        useful_when=[
            "target companies are easier to identify than target people",
        ],
        main_risks=["requires a second-stage workflow, not only a query list"],
    ),
    ExpansionParadigmRecipe(
        recipe_name="Diagnostic Contrast",
        description=(
            "Generates intentionally different expansions to expose whether "
            "failures come from recall, precision, source choice, constraints, "
            "or noise."
        ),
        paradigms=[
            ExpansionParadigm.intent_and_terminology,
            ExpansionParadigm.constraint_handling,
            ExpansionParadigm.source_lane_targeting,
            ExpansionParadigm.noise_control,
        ],
        useful_when=[
            "failure source is unknown",
            "we need contrast rather than a production strategy",
        ],
        main_risks=["not necessarily the best production strategy"],
    ),
]


B2B_CONTACT_DATA_EXPANSION_PARADIGM_MAP = ExpansionParadigmMap(
    recipes=B2B_CONTACT_DATA_EXPANSION_RECIPES
)
