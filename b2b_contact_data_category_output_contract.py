"""Pydantic contract for judging `b2b_contact_data` benchmark results.

This is a benchmark scoring contract, not a production API schema.
It defines result types, evidence modes, relevance grades, field credit,
field coverage, and common failure/noise tags for Task 1 evaluation.
"""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


B2BContactDataCategoryName = Literal["b2b_contact_data"]


class B2BContactDataEvidenceMode(str, Enum):
    """What evidence is available to the judge."""

    snippet_only = "snippet_only"
    content = "content"
    structured_enrichment = "structured_enrichment"


class B2BContactDataOutputItemType(str, Enum):
    """The type of returned item being judged."""

    person_profile = "person_profile"
    company_profile = "company_profile"
    mixed_person_company = "mixed_person_company"
    noise = "noise"


class B2BContactDataRelevanceGrade(IntEnum):
    """0-3 relevance grade used for nDCG@5."""

    irrelevant_or_noise = 0
    weak_or_partial = 1
    useful = 2
    excellent = 3


class B2BContactDataJudgeConfidence(str, Enum):
    """Judge confidence for a specific label or field credit."""

    low = "low"
    medium = "medium"
    high = "high"


class B2BContactDataFailureTag(str, Enum):
    """Common reasons a result is weak, noisy, or should be down-scored."""

    job_posting = "job_posting"
    career_advice = "career_advice"
    resume_template = "resume_template"
    hr_software_page = "hr_software_page"
    recruiting_software_page = "recruiting_software_page"
    staffing_agency_marketing = "staffing_agency_marketing"
    generic_hr_blog = "generic_hr_blog"
    unsupported_lead_directory = "unsupported_lead_directory"
    wrong_industry = "wrong_industry"
    wrong_geography = "wrong_geography"
    wrong_seniority = "wrong_seniority"
    wrong_entity_type = "wrong_entity_type"
    weak_evidence = "weak_evidence"
    missing_important_fields = "missing_important_fields"
    no_usable_evidence = "no_usable_evidence"
    private_contact_detail_required = "private_contact_detail_required"


class B2BContactDataMetricName(str, Enum):
    """Benchmark metrics this contract supports."""

    ndcg_at_5 = "ndcg_at_5"
    category_output_contract_coverage = "category_output_contract_coverage"
    hfte = "hfte"
    noise_rate = "noise_rate"


class B2BContactDataPersonField(str, Enum):
    """Creditable person-profile fields."""

    person_name = "person_name"
    current_title = "current_title"
    current_company = "current_company"
    profile_or_source_url = "profile_or_source_url"
    evidence_source = "evidence_source"
    location = "location"
    seniority = "seniority"
    department_or_function = "department_or_function"
    work_history = "work_history"
    tenure = "tenure"
    education = "education"
    skills = "skills"
    professional_summary = "professional_summary"


class B2BContactDataCompanyField(str, Enum):
    """Creditable company-profile fields."""

    company_name = "company_name"
    company_domain_or_profile_url = "company_domain_or_profile_url"
    industry_or_description = "industry_or_description"
    evidence_source = "evidence_source"
    headquarters_or_location = "headquarters_or_location"
    headcount_or_company_size = "headcount_or_company_size"
    funding = "funding"
    investors = "investors"
    employee_count = "employee_count"
    founded_year = "founded_year"
    growth_signal = "growth_signal"
    relevant_employee_or_profile_links = "relevant_employee_or_profile_links"


PERSON_CORE_FIELDS: List[B2BContactDataPersonField] = [
    B2BContactDataPersonField.person_name,
    B2BContactDataPersonField.current_title,
    B2BContactDataPersonField.current_company,
    B2BContactDataPersonField.profile_or_source_url,
    B2BContactDataPersonField.evidence_source,
]

PERSON_EXTRA_FIELDS: List[B2BContactDataPersonField] = [
    B2BContactDataPersonField.location,
    B2BContactDataPersonField.seniority,
    B2BContactDataPersonField.department_or_function,
    B2BContactDataPersonField.work_history,
    B2BContactDataPersonField.tenure,
    B2BContactDataPersonField.education,
    B2BContactDataPersonField.skills,
    B2BContactDataPersonField.professional_summary,
]

COMPANY_CORE_FIELDS: List[B2BContactDataCompanyField] = [
    B2BContactDataCompanyField.company_name,
    B2BContactDataCompanyField.company_domain_or_profile_url,
    B2BContactDataCompanyField.industry_or_description,
    B2BContactDataCompanyField.evidence_source,
]

COMPANY_EXTRA_FIELDS: List[B2BContactDataCompanyField] = [
    B2BContactDataCompanyField.headquarters_or_location,
    B2BContactDataCompanyField.headcount_or_company_size,
    B2BContactDataCompanyField.funding,
    B2BContactDataCompanyField.investors,
    B2BContactDataCompanyField.employee_count,
    B2BContactDataCompanyField.founded_year,
    B2BContactDataCompanyField.growth_signal,
    B2BContactDataCompanyField.relevant_employee_or_profile_links,
]


class B2BContactDataEvidenceBundle(BaseModel):
    """Evidence returned by retrieval or enrichment for one candidate."""

    mode: B2BContactDataEvidenceMode
    url: Optional[str] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    content: Optional[str] = None
    structured_fields: Dict[str, Any] = Field(default_factory=dict)
    source_name: Optional[str] = None


class B2BContactDataPublicContactHints(BaseModel):
    """Optional public contact hints.

    These are never required for relevance or field coverage.
    Record them only when explicitly visible in returned evidence and allowed
    by the applicable data handling policy.
    """

    email: Optional[str] = None
    phone: Optional[str] = None
    source_note: Optional[str] = None


class B2BContactDataPersonProfileFields(BaseModel):
    """Visible person-profile data for a candidate result."""

    person_name: Optional[str] = None
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    profile_or_source_url: Optional[str] = None
    evidence_source: Optional[str] = None
    location: Optional[str] = None
    seniority: Optional[str] = None
    department_or_function: Optional[str] = None
    work_history: List[str] = Field(default_factory=list)
    tenure: Optional[str] = None
    education: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    professional_summary: Optional[str] = None
    public_contact_hints: Optional[B2BContactDataPublicContactHints] = None


class B2BContactDataCompanyProfileFields(BaseModel):
    """Visible company-profile or firmographic data for a candidate result."""

    company_name: Optional[str] = None
    company_domain_or_profile_url: Optional[str] = None
    industry_or_description: Optional[str] = None
    evidence_source: Optional[str] = None
    headquarters_or_location: Optional[str] = None
    headcount_or_company_size: Optional[str] = None
    funding: Optional[str] = None
    investors: List[str] = Field(default_factory=list)
    employee_count: Optional[int] = None
    founded_year: Optional[int] = None
    growth_signal: Optional[str] = None
    relevant_employee_or_profile_links: List[str] = Field(default_factory=list)


class B2BContactDataCandidateResult(BaseModel):
    """A raw or partially structured candidate before judging."""

    item_type: B2BContactDataOutputItemType
    evidence: B2BContactDataEvidenceBundle
    person: Optional[B2BContactDataPersonProfileFields] = None
    company: Optional[B2BContactDataCompanyProfileFields] = None
    failure_tags: List[B2BContactDataFailureTag] = Field(default_factory=list)


class B2BContactDataCreditedField(BaseModel):
    """A field credited by the judge.

    The judge should credit a field only when it is visible in the returned
    evidence. `evidence_note` should point to the visible support, not world
    knowledge.
    """

    field_name: str
    evidence_mode: B2BContactDataEvidenceMode
    evidence_note: str
    confidence: B2BContactDataJudgeConfidence = B2BContactDataJudgeConfidence.medium


class B2BContactDataFieldCoverageScore(BaseModel):
    """Point-based field coverage score for one item type."""

    item_type: B2BContactDataOutputItemType
    credited_core_fields: List[str] = Field(default_factory=list)
    credited_extra_fields: List[str] = Field(default_factory=list)
    credited_points: int
    possible_points: int
    field_coverage: float


class B2BContactDataCoverageReport(BaseModel):
    """Coverage result.

    Mixed person/company items should report person and company coverage
    separately because the useful fields differ.
    """

    item_type: B2BContactDataOutputItemType
    person_coverage: Optional[B2BContactDataFieldCoverageScore] = None
    company_coverage: Optional[B2BContactDataFieldCoverageScore] = None


class B2BContactDataJudgedResult(BaseModel):
    """LLM-assisted or human-audited judgment for one candidate result."""

    item_type: B2BContactDataOutputItemType
    relevance_grade: B2BContactDataRelevanceGrade
    credited_fields: List[B2BContactDataCreditedField] = Field(default_factory=list)
    missing_important_fields: List[str] = Field(default_factory=list)
    failure_tags: List[B2BContactDataFailureTag] = Field(default_factory=list)
    evidence_note: str
    confidence: B2BContactDataJudgeConfidence
    coverage: B2BContactDataCoverageReport


class B2BContactDataRelevanceRubricItem(BaseModel):
    """Definition of one relevance grade."""

    grade: B2BContactDataRelevanceGrade
    label: str
    criteria: str


class B2BContactDataMetricUsage(BaseModel):
    """When a metric is valid for this contract."""

    metric: B2BContactDataMetricName
    valid_when: str
    notes: str


class B2BContactDataCategoryOutputContract(BaseModel):
    """Static contract definition for `b2b_contact_data` judging."""

    category: B2BContactDataCategoryName = "b2b_contact_data"
    item_types: List[B2BContactDataOutputItemType] = Field(
        default_factory=lambda: list(B2BContactDataOutputItemType)
    )
    evidence_modes: List[B2BContactDataEvidenceMode] = Field(default_factory=lambda: list(B2BContactDataEvidenceMode))
    person_core_fields: List[B2BContactDataPersonField] = Field(
        default_factory=lambda: list(PERSON_CORE_FIELDS)
    )
    person_extra_fields: List[B2BContactDataPersonField] = Field(
        default_factory=lambda: list(PERSON_EXTRA_FIELDS)
    )
    company_core_fields: List[B2BContactDataCompanyField] = Field(
        default_factory=lambda: list(COMPANY_CORE_FIELDS)
    )
    company_extra_fields: List[B2BContactDataCompanyField] = Field(
        default_factory=lambda: list(COMPANY_EXTRA_FIELDS)
    )
    contact_details_required: bool = False
    excluded_failure_tags: List[B2BContactDataFailureTag] = Field(
        default_factory=lambda: [
            B2BContactDataFailureTag.job_posting,
            B2BContactDataFailureTag.career_advice,
            B2BContactDataFailureTag.resume_template,
            B2BContactDataFailureTag.hr_software_page,
            B2BContactDataFailureTag.recruiting_software_page,
            B2BContactDataFailureTag.staffing_agency_marketing,
            B2BContactDataFailureTag.generic_hr_blog,
            B2BContactDataFailureTag.unsupported_lead_directory,
        ]
    )
    relevance_rubric: List[B2BContactDataRelevanceRubricItem] = Field(
        default_factory=lambda: [
            B2BContactDataRelevanceRubricItem(
                grade=B2BContactDataRelevanceGrade.excellent,
                label="excellent B2B result",
                criteria=(
                    "Correct entity type, matches query constraints, credible "
                    "source, and strong useful fields."
                ),
            ),
            B2BContactDataRelevanceRubricItem(
                grade=B2BContactDataRelevanceGrade.useful,
                label="useful B2B result",
                criteria=(
                    "Correct entity type and intent with enough visible evidence "
                    "to be useful, but some important fields are missing."
                ),
            ),
            B2BContactDataRelevanceRubricItem(
                grade=B2BContactDataRelevanceGrade.weak_or_partial,
                label="weak or partial result",
                criteria=(
                    "Related to the query, but missing important fields, weak "
                    "evidence, or only indirectly useful."
                ),
            ),
            B2BContactDataRelevanceRubricItem(
                grade=B2BContactDataRelevanceGrade.irrelevant_or_noise,
                label="irrelevant or noise",
                criteria=(
                    "Wrong entity type, job post, blog, marketing page, wrong "
                    "industry/geography, or no usable evidence."
                ),
            ),
        ]
    )
    metric_usage: List[B2BContactDataMetricUsage] = Field(
        default_factory=lambda: [
            B2BContactDataMetricUsage(
                metric=B2BContactDataMetricName.ndcg_at_5,
                valid_when=(
                    "Ranked candidates exist and each candidate has a 0-3 "
                    "relevance grade."
                ),
                notes="Uses B2BContactDataRelevanceGrade for the top ranked results.",
            ),
            B2BContactDataMetricUsage(
                metric=B2BContactDataMetricName.category_output_contract_coverage,
                valid_when="Returned evidence exposes creditable fields.",
                notes=(
                    "Uses field coverage. Do not credit fields that are not "
                    "visible in returned evidence."
                ),
            ),
            B2BContactDataMetricUsage(
                metric=B2BContactDataMetricName.hfte,
                valid_when=(
                    "Enriched or content payloads exist and token count can "
                    "be measured."
                ),
                notes=(
                    "Do not compute HFTE from expansion strings alone. "
                    "Snippet-only evidence is not enough for full HFTE."
                ),
            ),
            B2BContactDataMetricUsage(
                metric=B2BContactDataMetricName.noise_rate,
                valid_when="Any retrieval output exists.",
                notes="Count results marked noise or relevance grade 0.",
            ),
        ]
    )


def calculate_field_coverage(
    item_type: B2BContactDataOutputItemType,
    credited_person_fields: Optional[List[B2BContactDataPersonField]] = None,
    credited_company_fields: Optional[List[B2BContactDataCompanyField]] = None,
) -> B2BContactDataCoverageReport:
    """Calculate point-based field coverage for a judged result."""

    credited_person_fields = credited_person_fields or []
    credited_company_fields = credited_company_fields or []

    person_coverage: Optional[B2BContactDataFieldCoverageScore] = None
    company_coverage: Optional[B2BContactDataFieldCoverageScore] = None

    if item_type in (
        B2BContactDataOutputItemType.person_profile,
        B2BContactDataOutputItemType.mixed_person_company,
    ):
        person_coverage = _calculate_person_coverage(item_type, credited_person_fields)

    if item_type in (
        B2BContactDataOutputItemType.company_profile,
        B2BContactDataOutputItemType.mixed_person_company,
    ):
        company_coverage = _calculate_company_coverage(
            item_type, credited_company_fields
        )

    if item_type == B2BContactDataOutputItemType.noise:
        person_coverage = None
        company_coverage = None

    return B2BContactDataCoverageReport(
        item_type=item_type,
        person_coverage=person_coverage,
        company_coverage=company_coverage,
    )


def _calculate_person_coverage(
    item_type: B2BContactDataOutputItemType, credited_fields: List[B2BContactDataPersonField]
) -> B2BContactDataFieldCoverageScore:
    credited_set = set(credited_fields)
    credited_core = [field.value for field in PERSON_CORE_FIELDS if field in credited_set]
    credited_extra = [field.value for field in PERSON_EXTRA_FIELDS if field in credited_set]
    possible_points = len(PERSON_CORE_FIELDS) + len(PERSON_EXTRA_FIELDS)
    credited_points = len(credited_core) + len(credited_extra)

    return B2BContactDataFieldCoverageScore(
        item_type=item_type,
        credited_core_fields=credited_core,
        credited_extra_fields=credited_extra,
        credited_points=credited_points,
        possible_points=possible_points,
        field_coverage=_safe_ratio(credited_points, possible_points),
    )


def _calculate_company_coverage(
    item_type: B2BContactDataOutputItemType, credited_fields: List[B2BContactDataCompanyField]
) -> B2BContactDataFieldCoverageScore:
    credited_set = set(credited_fields)
    credited_core = [field.value for field in COMPANY_CORE_FIELDS if field in credited_set]
    credited_extra = [
        field.value for field in COMPANY_EXTRA_FIELDS if field in credited_set
    ]
    possible_points = len(COMPANY_CORE_FIELDS) + len(COMPANY_EXTRA_FIELDS)
    credited_points = len(credited_core) + len(credited_extra)

    return B2BContactDataFieldCoverageScore(
        item_type=item_type,
        credited_core_fields=credited_core,
        credited_extra_fields=credited_extra,
        credited_points=credited_points,
        possible_points=possible_points,
        field_coverage=_safe_ratio(credited_points, possible_points),
    )


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


B2B_CONTACT_DATA_CONTRACT = B2BContactDataCategoryOutputContract()
