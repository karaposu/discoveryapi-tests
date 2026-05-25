"""Runner configuration for the B2B contact-data experiment.

Edit the constants below to change how `runner.py` behaves. This module is
imported first by `runner.py`, so the `sys.path` bootstrap here runs before
any project or local-SDK imports.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent
SDK_SRC = Path("/Users/ns/Desktop/projects/sdk-python/src")

for import_path in (PROJECT_ROOT, SDK_SRC):
    import_path_text = str(import_path)
    if import_path_text not in sys.path:
        sys.path.insert(0, import_path_text)


from previous_attempt.expansion_schemas import ExpansionInputConstraintValue  # noqa: E402


# ---- Query selection ----

B2B_QUERY_EXAMPLES = [
    "VP Sales or Head of Sales at US cybersecurity SaaS startups in the United States",
    "Chief Revenue Officers at B2B fintech companies in New York",
    "Heads of Partnerships at Series A healthcare software companies in the United States",
    "People operations leaders at remote-first HR tech companies in the United States",
    "Founders or CEOs of B2B data infrastructure startups with 50-500 employees",
]

QUERY = B2B_QUERY_EXAMPLES[0]


# ---- Models and run-shape ----

PROMPT_VERSION = "b2b_contact_data_default_v1"

LLM_MODEL = "gpt-4o"
JUDGE_MODEL = "gpt-4o"

RESULT_COUNT = 10
JUDGE_TOP_N = 5
SKIP_JUDGE = False


# ---- SERP locale ----

LOCATION = "United States"
LANGUAGE = "en"
DEVICE = "desktop"


# ---- Bright Data ----

BRIGHTDATA_TOKEN: Optional[str] = None
SERP_ZONE: Optional[str] = None
AUTO_CREATE_ZONES = True


# ---- LLM input ----

DECLARED_CONSTRAINTS: List[ExpansionInputConstraintValue] = []


# ---- Output and source labels ----

BRIGHT_DATA_GOOGLE_SERP_SOURCE = "bright_data_google_serp"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"


# ---- Category-contract field lists ----

DEFAULT_TARGET_FIELDS = [
    "person_name",
    "current_title",
    "current_company",
    "profile_or_source_url",
    "evidence_source",
    "location",
    "seniority",
    "department_or_function",
    "work_history",
    "professional_summary",
    "company_name",
    "company_domain_or_profile_url",
    "industry_or_description",
    "headquarters_or_location",
    "headcount_or_company_size",
    "funding",
    "investors",
    "employee_count",
    "founded_year",
    "growth_signal",
    "relevant_employee_or_profile_links",
]


DEFAULT_EXCLUSIONS = [
    "job_postings",
    "career_advice",
    "resume_templates",
    "hr_software_pages",
    "recruiting_software_pages",
    "staffing_agency_marketing_pages",
    "generic_hr_blogs",
    "unsupported_lead_directories",
]
