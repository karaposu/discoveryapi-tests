# Expansion Benchmark — Visualisation

**Source report:** `minimal4_20260520_104200_scored.json`
**Started:** `2026-05-20T10:42:00.497854+00:00`  
**Completed:** `2026-05-20T10:43:04.026277+00:00`  
**Elapsed:** 63.528423 seconds

---

## Query

> **VP Sales or Head of Sales at US cybersecurity SaaS startups in the United States**

### Structured spec

| Field | Value |
|---|---|
| entity_type | `person_profile` |
| industry | `cybersecurity SaaS` |
| geography | `United States` |
| company_type | `startup` |
| company_size_or_stage | `—` |
| role_title_family | `sales_leadership` |
| seniority_band | `vp` |
| department_or_function | `sales` |

---

## Expansions used

The LLM was asked to produce variants seeded by **4 paradigms**, plus a verbatim baseline added by Python. Total: **13 variants** (3 per LLM seed + 1 verbatim).

### Seed paradigms

| Seed | Variants | What it does |
|---|---|---|
| `verbatim` | 1 | Baseline. Renders the natural query unchanged (Python-built, no LLM). |
| `title_broadening` | 3 | Broaden the role/title term with synonyms (e.g. *VP Sales* → *(VP Sales OR Head of Sales OR CRO)*). |
| `industry_broadening` | 3 | Broaden the industry/domain term with synonyms (e.g. *cybersecurity SaaS* → *(cybersecurity SaaS OR security software)*). |
| `geography_broadening` | 3 | Broaden the geography term with alternatives (e.g. *United States* → *(United States OR USA)*). |
| `combined_broadening` | 3 | Combine two or more of the above broadenings simultaneously. |

---

## Results per expansion category

Each variant inside a category was run as one SERP query producing 5 candidates. **Bolded scores** are LLM judge `total_point` values (0-10, sum of 10 boolean question True answers).

### `verbatim`  —  category mean **3.8/10**  ·  1 variant(s)

#### Variant 1 — mean **3.8/10**  ·  max **10/10**  ·  sum **19/50**

**Query:**

```
VP Sales or Head of Sales at US cybersecurity SaaS startups in the United States
```

*Rationale: Baseline: the natural query without any broadening.*

**SERP results:**

**1. Score: 5/10**  — [https://aspironsearch.com/jobs/head-of-sales-series-a-cybersecurity/](https://aspironsearch.com/jobs/head-of-sales-series-a-cybersecurity/)

- *Title:* Head of Sales Role | Series A Cybersecurity
- *Snippet:* VendorExplore the Head of Sales role at a Series A cybersecurity company. Learn key responsibilities, leadership expectations, and growth opportunities.

**2. Score: 1/10**  — [https://www.indeed.com/q-vice-president-of-sales-cyber-security-jobs.html](https://www.indeed.com/q-vice-president-of-sales-cyber-security-jobs.html)

- *Title:* Vice President of Sales Cyber Security Jobs, Employment
- *Snippet:* 822 Vice President of Sales Cyber Security jobs available on Indeed.com. Apply to Vice President, Vice President of Sales, Vice President, Product Manager ...

**3. Score: 10/10**  — [https://www.linkedin.com/in/jimmy-phipps-797a6162](https://www.linkedin.com/in/jimmy-phipps-797a6162)

- *Title:* Jimmy Phipps - Scaling SaaS & Cybersecurity Companies
- *Snippet:* Jimmy Phipps · VP of Sales | Scaling SaaS & Cybersecurity Companies | GTM Builder | Enterprise Growth Leader | MEDDPICC · View mutual connections with Jimmy.

**4. Score: 2/10**  — [https://www.ziprecruiter.com/Jobs/Saas-Sales-Cybersecurity](https://www.ziprecruiter.com/Jobs/Saas-Sales-Cybersecurity)

- *Title:* Saas Sales Cybersecurity Jobs (NOW HIRING)
- *Snippet:* Browse 1000+ SAAS SALES CYBERSECURITY jobs ($35k-$80k) from companies with openings that are hiring now. Find job postings near you and ...

**5. Score: 1/10**  — [https://www.builtinnyc.com/jobs/sales/cybersecurity](https://www.builtinnyc.com/jobs/sales/cybersecurity)

- *Title:* Best Cybersecurity Sales Jobs in New York City, NY 2026
- *Snippet:* Search the best Cybersecurity Sales Jobs from top companies & startups in New York City, NY. New jobs added daily.

---

### `title_broadening`  —  category mean **3.33/10**  ·  3 variant(s)

#### Variant 2 — mean **4.8/10**  ·  max **10/10**  ·  sum **24/50**

**Query:**

```
("VP Sales" OR "Vice President of Sales" OR "Sales VP") "cybersecurity SaaS" "United States"
```

*Rationale: This variant broadens the title to include full forms and alternative phrasings of 'VP Sales'.*

**SERP results:**

**1. Score: 10/10**  — [https://www.linkedin.com/in/rudyricci](https://www.linkedin.com/in/rudyricci)

- *Title:* Rudy Ricci - VP Sales | Cybersecurity SaaS
- *Snippet:* VP Sales | Cybersecurity SaaS | CRO-Scope GTM Leadership | BeyondTrust ... United States · 500+ connections on LinkedIn. View Rudy Ricci's profile on ...

**2. Score: 9/10**  — [https://careersteer.com/jobs/listing/austin-texas-united-states/hypori/vice-president-of-sales/k5739ppnsgv0ybpna7m59pfc5585m0x8](https://careersteer.com/jobs/listing/austin-texas-united-states/hypori/vice-president-of-sales/k5739ppnsgv0ybpna7m59pfc5585m0x8)

- *Title:* Vice President of Sales at Hypori - Austin, Texas, United States
- *Snippet:* ... Vice President of Sales position at Hypori in Austin, Texas, United States ... cybersecurity / saas, based in Austin, Texas, United States.Read more

**3. Score: 1/10**  — [https://www.glassdoor.com/Job/sales-vp-saas-jobs-SRCH_KO0,13.htm](https://www.glassdoor.com/Job/sales-vp-saas-jobs-SRCH_KO0,13.htm)

- *Title:* 1424 Sales vp saas jobs in United States
- *Snippet:* 1,424 Sales vp saas jobs in United States. Most ... 5+ years in B2B sales, preferably within cybersecurity, SaaS, or MSSP…&hellip; ... People who searched for jobs ...

**4. Score: 3/10**  — [https://builtin.com/job/vp-sales-west-enterprise/7734544](https://builtin.com/job/vp-sales-west-enterprise/7734544)

- *Title:* VP Sales, West Enterprise - BeyondTrust
- *Snippet:* VP Sales, West Enterprise ... cybersecurity SaaS portfolio. Our culture of ... Staff Software Engineer. Fintech • Software. Remote or Hybrid. United States. 1750 ...

**5. Score: 1/10**  — [https://www.builtinboston.com/jobs/sales/senior/cybersecurity](https://www.builtinboston.com/jobs/sales/senior/cybersecurity)

- *Title:* Top Senior Level Cybersecurity Sales Jobs in Boston, MA
- *Snippet:* VP Sales, Commercial. Reposted 3 Days AgoSaved. Easy Apply. Remote or Hybrid ... United States. 350K-380K Annually. Senior level. 350K-380K Annually. Senior ...Read more

---

#### Variant 3 — mean **3.8/10**  ·  max **8/10**  ·  sum **19/50**

**Query:**

```
("Head of Sales" OR "Sales Director" OR "Sales Leader") "cybersecurity SaaS" "United States"
```

*Rationale: This variant broadens the title to include functional synonyms for 'Head of Sales'.*

**SERP results:**

**1. Score: 3/10**  — [https://www.ziprecruiter.com/Jobs/Saas-Sales-Director-Remote/-in-Washington,DC](https://www.ziprecruiter.com/Jobs/Saas-Sales-Director-Remote/-in-Washington,DC)

- *Title:* $79k-$186k Saas Sales Director Remote Jobs in Washington, DC
- *Snippet:* Sales Director (Cybersecurity SaaS) ... United States. HOURS & TIME ZON E: Monday ... All JobsAll Jobs Saas Sales Director Remote JobsSaas Sales ...

**2. Score: 1/10**  — [https://www.whatjobs.com/jobs/sales-director-cybersecurity-saas?id=2652796632](https://www.whatjobs.com/jobs/sales-director-cybersecurity-saas?id=2652796632)

- *Title:* What Sales Director Cybersecurity Saas Jobs Are Near Me?
- *Snippet:* What Sales Director Cybersecurity Saas Jobs are in the United States? Showing 0 Sales Director Cybersecurity Saas jobs in the United States. Sorry to hear ...

**3. Score: 4/10**  — [https://www.talent.com/view?id=610994345465939378](https://www.talent.com/view?id=610994345465939378)

- *Title:* Sales Director (Cybersecurity SaaS) – Iopa Solutions
- *Snippet:* Sales Director (Cybersecurity SaaS). Iopa Solutions • Washington, DC, United States. 30+ days ago.

**4. Score: 8/10**  — [https://www.linkedin.com/in/tedwintz](https://www.linkedin.com/in/tedwintz)

- *Title:* Ted Wintz - Proven Sales Leader I CyberSecurity/Saas ...
- *Snippet:* Proven Sales Leader I CyberSecurity/Saas Services I Driving Revenue Growth I Enterprise Account Management ... San Diego County, California, United States.Read more

**5. Score: 3/10**  — [https://www.remoterocketship.com/us/company/axonius/jobs/area-sales-director-florida-remote/](https://www.remoterocketship.com/us/company/axonius/jobs/area-sales-director-florida-remote/)

- *Title:* Area Sales Director at Axonius - United States Remote
- *Snippet:* ... cybersecurity, SaaS, or cloud technology sectors. • Documented track ... Technical Sales Leader for national accounts at G&G Industrial Lighting.Read more

---

#### Variant 4 — mean **1.4/10**  ·  max **2/10**  ·  sum **7/50**

**Query:**

```
("Chief Sales Officer" OR "CSO" OR "Sales Executive") "cybersecurity SaaS" "United States"
```

*Rationale: This variant broadens the title to include C-suite forms and executive-level synonyms.*

**SERP results:**

**1. Score: 2/10**  — [https://www.jobleads.com/us/job/enterprise-cybersecurity-saas-sales-executive--united-states--e395a6733881e9bdc2f3150778aa5de52](https://www.jobleads.com/us/job/enterprise-cybersecurity-saas-sales-executive--united-states--e395a6733881e9bdc2f3150778aa5de52)

- *Title:* Enterprise Cybersecurity SaaS Sales Executive
- *Snippet:* DeleteMe is hiring Enterprise Cybersecurity SaaS Sales Executive in United States. Apply now with JobLeads!

**2. Score: 1/10**  — [https://www.linkedin.com/jobs/view/cybersecurity-lead-generation-sales-executive-100%25-commission-at-xcigence-4400942702](https://www.linkedin.com/jobs/view/cybersecurity-lead-generation-sales-executive-100%25-commission-at-xcigence-4400942702)

- *Title:* Cybersecurity Lead Generation & Sales Executive (100% ...
- *Snippet:* Proven track record in cybersecurity, SaaS, or enterprise technology sales ... Get notified about new Lead Generation Executive jobs in United States. Sign ...Read more

**3. Score: 2/10**  — [https://www.talent.com/view?id=614256909993771732](https://www.talent.com/view?id=614256909993771732)

- *Title:* Senior MSP Cybersecurity SaaS Sales Executive
- *Snippet:* Senior MSP Cybersecurity SaaS Sales Executive. Senior MSP Cybersecurity SaaS Sales Executive. Inforcer • Cerritos, CA, United States. 11 days ago. Apply.

**4. Score: 1/10**  — [https://www.builtinla.com/jobs/remote/sales/search/sales-executive?page=3](https://www.builtinla.com/jobs/remote/sales/search/sales-executive?page=3)

- *Title:* Best Remote Sales Executive Jobs in Los Angeles, CA 2026
- *Snippet:* Enterprise Sales Executive. Reposted 6 Days AgoSaved. Remote. United States of America. 170K-180K Annually. Expert/Leader. 170K-180K Annually. Expert/Leader.Read more

**5. Score: 1/10**  — [https://workinvirtual.com/job/enterprise-account-executive-cybersecurity-saas-channel-sales-enterprise-growth-us-remote-central-east-75k-125k-uncapped-commission/](https://workinvirtual.com/job/enterprise-account-executive-cybersecurity-saas-channel-sales-enterprise-growth-us-remote-central-east-75k-125k-uncapped-commission/)

- *Title:* Cybersecurity SaaS, Channel Sales & Enterprise Growth
- *Snippet:* ... Cybersecurity SaaS, Channel Sales ... sales executive usa, software sales executive usa ... United States, Canada (Remote); Praia Health; Full ...

---

### `industry_broadening`  —  category mean **3.47/10**  ·  3 variant(s)

#### Variant 5 — mean **3.2/10**  ·  max **4/10**  ·  sum **16/50**

**Query:**

```
("VP Sales" OR "Head of Sales") "cybersecurity" "United States"
```

*Rationale: This variant broadens the industry to include the general 'cybersecurity' sector.*

**SERP results:**

**1. Score: 3/10**  — [https://www.linkedin.com/jobs/vp-sales-cybersecurity-jobs](https://www.linkedin.com/jobs/vp-sales-cybersecurity-jobs)

- *Title:* 361 Vp Sales Cybersecurity jobs in United States
- *Snippet:* Today's top 361 Vp Sales Cybersecurity jobs in United States. Leverage your ... Head of Sales and Business Development jobs · Sales Director jobs · Chief ...Read more

**2. Score: 3/10**  — [https://www.linkedin.com/jobs/vp-sales-cybersecurity-jobs-new-york-ny](https://www.linkedin.com/jobs/vp-sales-cybersecurity-jobs-new-york-ny)

- *Title:* 26 Vp Sales Cybersecurity jobs in New York ...
- *Snippet:* Get notified about new Vp Sales Cybersecurity jobs in New York, New York, United States. ... Head of Sales and Business Development jobs · Sales Director ...Read more

**3. Score: 3/10**  — [https://startup.jobs/vp-sales-central-safe-security-5327175](https://startup.jobs/vp-sales-central-safe-security-5327175)

- *Title:* VP Sales, Central at Safe Security
- *Snippet:* Apply now for VP Sales, Central job at Safe Security (REMOTE). ––– Ready to join a rocket ship that is revolutionizing the cyber risk management industry?

**4. Score: 4/10**  — [https://www.builtinnyc.com/job/vice-president-international-head-sales-strategy/8750039](https://www.builtinnyc.com/job/vice-president-international-head-sales-strategy/8750039)

- *Title:* Vice President International Head of Sales Strategy
- *Snippet:* The Head of Sales Strategy and Vertical Expansion is responsible for driving revenue growth through the development and execution of ...Read more

**5. Score: 3/10**  — [https://jobright.ai/jobs/cybersecurity-co-founder-head-of-sales-(100-remote)-(m-f-d)-jobs-in-united-states](https://jobright.ai/jobs/cybersecurity-co-founder-head-of-sales-(100-remote)-(m-f-d)-jobs-in-united-states)

- *Title:* Cybersecurity Co Founder Head Of Sales (100 Remote) (m F D) ...
- *Snippet:* Best Cybersecurity Co Founder Head Of Sales (100 Remote) (m F D) jobs available in United States on jobright.ai. Apply to Cybersecurity Co Founder Head Of Sales

---

#### Variant 6 — mean **1.6/10**  ·  max **4/10**  ·  sum **8/50**

**Query:**

```
("VP Sales" OR "Head of Sales") "SaaS" "United States"
```

*Rationale: This variant focuses on the broader 'SaaS' industry, removing the specific 'cybersecurity' focus.*

**SERP results:**

**1. Score: 1/10**  — [https://www.linkedin.com/jobs/vp-sales-saas-jobs](https://www.linkedin.com/jobs/vp-sales-saas-jobs)

- *Title:* 1000+ Vp Sales Saas jobs in United States
- *Snippet:* Today's top 1000+ Vp Sales Saas jobs in United States. Leverage your ... Head of Sales and Business Development jobs · Sales Director jobs · Chief Revenue ...Read more

**2. Score: 1/10**  — [https://www.glassdoor.com/Job/vp-sales-saas-jobs-SRCH_KO0,13.htm](https://www.glassdoor.com/Job/vp-sales-saas-jobs-SRCH_KO0,13.htm)

- *Title:* 1621 Vp sales saas jobs in United States
- *Snippet:* 1,621 Vp sales saas jobs in United States. Most relevant. Throttlenet. Senior Sales Associate. Saint Louis, MO. $130K - $180K (Employer provided). Easy Apply.Read more

**3. Score: 1/10**  — [https://www.ziprecruiter.com/Salaries/Vp-Sales-Saas-Salary](https://www.ziprecruiter.com/Salaries/Vp-Sales-Saas-Salary)

- *Title:* Salary: Vp Sales Saas (May, 2026) United States
- *Snippet:* The average VP SALES SAAS SALARY in the United States as of May 2026 is $79.77 an hour or $165921 per year. Get paid what you're worth!

**4. Score: 1/10**  — [https://www.indeed.com/q-head-of-sales-saas-ai-jobs.html](https://www.indeed.com/q-head-of-sales-saas-ai-jobs.html)

- *Title:* Head of Sales Saas Ai Jobs, Employment
- *Snippet:* ... Head of Sales Saas Ai jobs available on Indeed.com. Apply to Account ... VP Sales. Easily apply. DualEntry. United States. $250,000 - $350,000 a year.Read more

**5. Score: 4/10**  — [https://www.thesaasjobs.com/jobs/468282519-vp-sales-americas](https://www.thesaasjobs.com/jobs/468282519-vp-sales-americas)

- *Title:* VP Sales, Americas at Cohere
- *Snippet:* The SaaS Jobs · Jobs · Companies · Profiles · Pricing ... VP Sales ... United States) • $239k - $265k / year • 3d ago. Sales Senior level. 3d ago. Apply. Pigment ...

---

#### Variant 7 — mean **5.6/10**  ·  max **8/10**  ·  sum **28/50**

**Query:**

```
("VP Sales" OR "Head of Sales") "tech startups" "United States"
```

*Rationale: This variant broadens the industry to include 'tech startups' as a general category.*

**SERP results:**

**1. Score: 8/10**  — [https://www.linkedin.com/in/simonbrief](https://www.linkedin.com/in/simonbrief)

- *Title:* Simon B. - Head of Sales for Startups @ Google Cloud
- *Snippet:* Head of Sales for Startups @ Google Cloud. Google NYU Stern School of Business. New York, New York, United States. 2K followers 500+ connections. See your ...Read more

**2. Score: 1/10**  — [https://www.ziprecruiter.com/Jobs/Head-Of-Startups](https://www.ziprecruiter.com/Jobs/Head-Of-Startups)

- *Title:* $50k-$95k Head Of Startups Jobs (NOW HIRING) May 2026
- *Snippet:* Head of Sales - Hands-On Closer & Team Builder [Confidential SaaS ... years of experience in growth or product marketing within tech startups and ...Read more

**3. Score: 7/10**  — [https://wellfound.com/jobs/1279026-head-of-sales-saas-sales-veteran](https://wellfound.com/jobs/1279026-head-of-sales-saas-sales-veteran)

- *Title:* Head of sales - SaaS sales veteran at Shake • New York City
- *Snippet:* Shake is hiring a Head of sales - SaaS sales veteran in New York City and United States - Apply now on Wellfound ... Tech Startups · Remote. For Recruiters ...Read more

**4. Score: 4/10**  — [https://joseflegal.com/careers/head-of-sales-north-america/](https://joseflegal.com/careers/head-of-sales-north-america/)

- *Title:* We're hiring a Head of Sales (North America) | Careers at Josef | Josef
- *Snippet:* Head of Sales (North America) ... United States or Canada (distributed team, so flexible on exact location) ... This is a transformative opportunity to play a ...

**5. Score: 8/10**  — [https://www.linkedin.com/in/alexyusalesleadermba](https://www.linkedin.com/in/alexyusalesleadermba)

- *Title:* Alex Y - VP Sales | Head of Sales | SaaS, AI, Fintech ...
- *Snippet:* VP Sales | Head of Sales | SaaS, AI, Fintech, Healthtech. Head X Group University of Arizona. Rancho Cordova, California, United States. 2K followers 500+ ...Read more

---

### `geography_broadening`  —  category mean **4.8/10**  ·  3 variant(s)

#### Variant 8 — mean **3.4/10**  ·  max **10/10**  ·  sum **17/50**

**Query:**

```
("VP Sales" OR "Head of Sales") "cybersecurity SaaS" ("USA" OR "US")
```

*Rationale: This variant broadens the geography to include common abbreviations for the United States.*

**SERP results:**

**1. Score: 10/10**  — [https://www.linkedin.com/in/rudyricci](https://www.linkedin.com/in/rudyricci)

- *Title:* Rudy Ricci - VP Sales | Cybersecurity SaaS
- *Snippet:* VP Sales | Cybersecurity SaaS | CRO-Scope GTM Leadership | BeyondTrust ... US, UK, and Middle East. Operating as de facto CRO, I align Sales, Marketing ...Read more

**2. Score: 2/10**  — [https://bebee.com/us/jobs/head-of-sales-vc-backed-b2b-cybersecurity-saas-new-york-hybrid-harmonic-finance-inc-certified-b-corp--theirstack-652165623](https://bebee.com/us/jobs/head-of-sales-vc-backed-b2b-cybersecurity-saas-new-york-hybrid-harmonic-finance-inc-certified-b-corp--theirstack-652165623)

- *Title:* VC-Backed B2B Cybersecurity SaaS | New York (Hybrid)
- *Snippet:* Head of Sales | VC-Backed B2B Cybersecurity SaaS | New York (Hybrid)** *The ... U.S. expansion while pursuing personal quota. The ideal candidate has a ...Read more

**3. Score: 1/10**  — [https://www.ziprecruiter.com/Jobs/Saas-Sales-Cybersecurity/--in-Washington](https://www.ziprecruiter.com/Jobs/Saas-Sales-Cybersecurity/--in-Washington)

- *Title:* Saas Sales Cybersecurity Jobs in Washington (NOW HIRING)
- *Snippet:* Demonstrated track record of selling Cloud Cybersecurity SaaS solutions to U.S. Federal government ... Manager, Sales Engineer (Federal-DOD).

**4. Score: 1/10**  — [https://www.reddit.com/r/sales/comments/18lqbsk/saas_cyber_security_bdrsreps_whats_working_for/](https://www.reddit.com/r/sales/comments/18lqbsk/saas_cyber_security_bdrsreps_whats_working_for/)

- *Title:* SaaS Cyber Security BDR's/reps - what's working for white ...
- *Snippet:* Can someone explain the thesis to me of how AI will replace cybersecurity, SaaS stocks, etc.? ... us like toddlers who just learned object ...Read more

**5. Score: 3/10**  — [https://www.linkedin.com/posts/renebystron_cybersecurity-hiring-vpofsales-activity-7396186370823692288-3Sdq](https://www.linkedin.com/posts/renebystron_cybersecurity-hiring-vpofsales-activity-7396186370823692288-3Sdq)

- *Title:* Cybersecurity VP of Sales roles up to 558k: 8 US SaaS ...
- *Snippet:* ... head of sales roles in cybersecurity, add them in the comments so ... Here are 8 US based cybersecurity SaaS roles for senior sales ...Read more

---

#### Variant 9 — mean **6.0/10**  ·  max **10/10**  ·  sum **30/50**

**Query:**

```
("VP Sales" OR "Head of Sales") "cybersecurity SaaS" "North America"
```

*Rationale: This variant broadens the geography to include the regional term 'North America'.*

**SERP results:**

**1. Score: 10/10**  — [https://www.linkedin.com/in/rudyricci](https://www.linkedin.com/in/rudyricci)

- *Title:* Rudy Ricci - VP Sales | Cybersecurity SaaS
- *Snippet:* VP Sales | Cybersecurity SaaS | CRO-Scope GTM Leadership | BeyondTrust ... North America. This was formative in ways that still drive how I lead today ...Read more

**2. Score: 1/10**  — [https://www.ziprecruiter.com/Jobs/Saas-Sales-Director-Remote/-in-Toronto,ON](https://www.ziprecruiter.com/Jobs/Saas-Sales-Director-Remote/-in-Toronto,ON)

- *Title:* Saas Sales Director Remote Jobs in Toronto, ON (NOW HIRING)
- *Snippet:* ... the cybersecurity, SaaS ... Director, Sales REPORTS TO: VP, Sales Cority is the global enterprise EHS software provider ... ... Senior Director of Sales - ...

**3. Score: 10/10**  — [https://www.craigwirwin.com/](https://www.craigwirwin.com/)

- *Title:* Craig W. Irwin — CRO & VP Sales | AI-Native Revenue ...
- *Snippet:* Cybersecurity SaaS, $0 to $27M ARR, Enterprise SaaS category creation. ACV ... Apica VP Sales and COO North America, Performance SaaS, $0 to $10M ARR in 18 ...Read more

**4. Score: 8/10**  — [https://dk.linkedin.com/in/magnuscohn](https://dk.linkedin.com/in/magnuscohn)

- *Title:* Magnus Cohn - Commercial Leader | CRO / VP Sales
- *Snippet:* ... North America, APAC, and LATAM ... Let's connect if you're building or scaling a commercial organization. Keywords: CRO, VP Sales, CCO, Head of Sales ...Read more

**5. Score: 1/10**  — [https://www.talent.com/view?id=613765230344275387](https://www.talent.com/view?id=613765230344275387)

- *Title:* Head of Sales Engineering - North America (Remote) – EDB
- *Snippet:* Head of Sales ... North America. This role focuses on ... Head of Demand Generation | Cybersecurity SaaS ...

---

#### Variant 10 — mean **5.0/10**  ·  max **10/10**  ·  sum **25/50**

**Query:**

```
("VP Sales" OR "Head of Sales") "cybersecurity SaaS" ("California" OR "New York" OR "Texas")
```

*Rationale: This variant broadens the geography to include specific state-level alternatives.*

**SERP results:**

**1. Score: 3/10**  — [https://bebee.com/us/jobs/head-of-sales-vc-backed-b2b-cybersecurity-saas-new-york-hybrid-harmonic-finance-inc-certified-b-corp--theirstack-652165623](https://bebee.com/us/jobs/head-of-sales-vc-backed-b2b-cybersecurity-saas-new-york-hybrid-harmonic-finance-inc-certified-b-corp--theirstack-652165623)

- *Title:* VC-Backed B2B Cybersecurity SaaS | New York (Hybrid)
- *Snippet:* *Head of Sales | VC-Backed B2B Cybersecurity SaaS | New York (Hybrid); *The Client. Our client is revolutionizing application security with an AI-powered ...Read more

**2. Score: 10/10**  — [https://www.linkedin.com/in/rudyricci](https://www.linkedin.com/in/rudyricci)

- *Title:* Rudy Ricci - VP Sales | Cybersecurity SaaS
- *Snippet:* VP Sales | Cybersecurity SaaS | CRO-Scope GTM Leadership | BeyondTrust ... Your California Privacy Choices · Cookie Policy · Copyright Policy · Brand Policy ...Read more

**3. Score: 0/10**  — [https://www.ziprecruiter.com/Jobs/Vice-President-Unlimited-Pto/-in-New-York-City,NY](https://www.ziprecruiter.com/Jobs/Vice-President-Unlimited-Pto/-in-New-York-City,NY)

- *Title:* Vice President Unlimited Pto Jobs in New York City, NY
- *Snippet:* VP Marketing: Growth, Brand & Demand for Cybersecurity SaaS ... VP Sales, East · New York, NY. $250K - $300K/yr ... California Privacy Notice · Terms ...

**4. Score: 8/10**  — [https://www.reval.site/u/mark-ousley](https://www.reval.site/u/mark-ousley)

- *Title:* Mark Ousley - Executive sales leader specializing in SaaS ...
- *Snippet:* Experience. Head of SalesCo-Active Training Institute · Aug 2025 – Present. Head of SalesAnalyze Corporation · Feb 2023 – Aug 2025. Director of Key Accounts ...Read more

**5. Score: 4/10**  — [https://www.linkedin.com/jobs/view/head-of-sales-vc-backed-b2b-cybersecurity-saas-new-york-hybrid-at-harmonic-finance-inc-%E2%84%A2-certified-b-corp-4379668429](https://www.linkedin.com/jobs/view/head-of-sales-vc-backed-b2b-cybersecurity-saas-new-york-hybrid-at-harmonic-finance-inc-%E2%84%A2-certified-b-corp-4379668429)

- *Title:* Certified B Corp hiring Head of Sales | VC-Backed B2B ...
- *Snippet:* Head of Sales | VC-Backed B2B Cybersecurity SaaS | New York (Hybrid) ... Senior Director/VP, Sales Operations ... Your California Privacy Choices · Cookie Policy ...

---

### `combined_broadening`  —  category mean **2.13/10**  ·  3 variant(s)

#### Variant 11 — mean **2.0/10**  ·  max **4/10**  ·  sum **10/50**

**Query:**

```
("VP Sales" OR "Sales Director") "cybersecurity" ("USA" OR "North America")
```

*Rationale: This variant combines title and geography broadening by using synonyms for 'VP Sales' and regional terms for the US.*

**SERP results:**

**1. Score: 3/10**  — [https://www.linkedin.com/jobs/vp-sales-cybersecurity-jobs](https://www.linkedin.com/jobs/vp-sales-cybersecurity-jobs)

- *Title:* 339 Vp Sales Cybersecurity jobs in United States
- *Snippet:* United States. Leverage your professional network, and get hired. New Vp Sales Cybersecurity jobs added daily ... VP, Sales (North America). Stealth. San ...Read more

**2. Score: 1/10**  — [https://www.indeed.com/q-vice-president-of-sales-cyber-security-jobs.html](https://www.indeed.com/q-vice-president-of-sales-cyber-security-jobs.html)

- *Title:* Vice President of Sales Cyber Security Jobs, Employment
- *Snippet:* Konica Minolta Business Solutions, U.S.A., Inc. Remote in Houston, TX 77079 ... Cybersecurity Pre Sales Director. Tata Consultancy Services. Dallas, TX.Read more

**3. Score: 1/10**  — [https://talents.vaia.com/companies/macrohire/sales-director-north-america-cybersecurity-services-39227967/](https://talents.vaia.com/companies/macrohire/sales-director-north-america-cybersecurity-services-39227967/)

- *Title:* Sales Director, North America – Cybersecurity Services
- *Snippet:* The predicted salary is between 72000 - 108000 $ per year. Sales Director, North America – Cybersecurity Services We are hiring a Sales Director (Hunter + ...Read more

**4. Score: 1/10**  — [https://www.ziprecruiter.com/Jobs/Cyber-Security-Sales/-in-Boston,MA](https://www.ziprecruiter.com/Jobs/Cyber-Security-Sales/-in-Boston,MA)

- *Title:* Cyber Security Sales Jobs in Boston, MA (NOW HIRING)
- *Snippet:* Sales Director, North America - Cybersecurity Services We are hiring a Sales Director (Hunter + Account Manager) with 10-12 years of ...Read more

**5. Score: 4/10**  — [https://builtin.com/job/enterprise-sales-director-cybersecurity-north-america/3755176](https://builtin.com/job/enterprise-sales-director-cybersecurity-north-america/3755176)

- *Title:* Enterprise Sales Director - Cybersecurity (North America)
- *Snippet:* SandboxAQ is hiring for a Remote Enterprise Sales Director - Cybersecurity (North America) in USA. Find more details about the job and how to apply at Built In.

---

#### Variant 12 — mean **1.8/10**  ·  max **3/10**  ·  sum **9/50**

**Query:**

```
("Head of Sales" OR "Sales Executive") "SaaS" "United States"
```

*Rationale: This variant combines title and industry broadening by using synonyms for 'Head of Sales' and focusing on the broader 'SaaS' industry.*

**SERP results:**

**1. Score: 2/10**  — [https://www.linkedin.com/jobs/saas-sales-executive-jobs](https://www.linkedin.com/jobs/saas-sales-executive-jobs)

- *Title:* 1000+ Saas Sales Executive jobs in United States
- *Snippet:* Today's top 1000+ Saas Sales Executive jobs in United States. Leverage your professional network, and get hired. New Saas Sales Executive jobs added daily.

**2. Score: 1/10**  — [https://www.indeed.com/q-saas-sales-executive-l-austin,-tx-jobs.html](https://www.indeed.com/q-saas-sales-executive-l-austin,-tx-jobs.html)

- *Title:* Saas Sales Executive Jobs, Employment in Austin, TX
- *Snippet:* ... Saas Sales Executive jobs available in Austin, TX on Indeed.com. Apply ... United States Home Services. Austin, TX 78701. $150,000 - $200,000 a year.Read more

**3. Score: 3/10**  — [https://careers.jacobs.com/en_US/careers/JobDetail/SMB-SaaS-Sales-Executive-Private-Sector/38877](https://careers.jacobs.com/en_US/careers/JobDetail/SMB-SaaS-Sales-Executive-Private-Sector/38877)

- *Title:* SMB SaaS Sales Executive, Private Sector
- *Snippet:* SMB SaaS Sales Executive, Private Sector. Dallas, Texas, United States | 38877 | Transportation | Digital and Data | Multiple Locations.Read more

**4. Score: 2/10**  — [https://www.ziprecruiter.com/Jobs/Saas-Sales-Executive](https://www.ziprecruiter.com/Jobs/Saas-Sales-Executive)

- *Title:* Saas Sales Executive Jobs (NOW HIRING)
- *Snippet:* As of May 17, 2026, the average yearly pay for saas sales executive in the United States is $82,500.00, according to ZipRecruiter salary data.Read more

**5. Score: 1/10**  — [https://bebee.com/us/jobs/role/saas-sales-executive](https://bebee.com/us/jobs/role/saas-sales-executive)

- *Title:* 148112+ Saas Sales Executive Jobs in United States 2026
- *Snippet:* The estimated salary for Saas Sales Executive in United States ranges from $105,000 to $145,000 USD per year, depending on experience and location. How many ...

---

#### Variant 13 — mean **2.6/10**  ·  max **6/10**  ·  sum **13/50**

**Query:**

```
("Chief Sales Officer" OR "CSO") "tech startups" ("USA" OR "California")
```

*Rationale: This variant combines title, industry, and geography broadening by using C-suite titles, general tech startups, and specific US locations.*

**SERP results:**

**1. Score: 1/10**  — [https://www.cast-usa.com/chief-sales-officer-jobs-in-atlanta](https://www.cast-usa.com/chief-sales-officer-jobs-in-atlanta)

- *Title:* Recruitment Agency For Chief Sales Officer Jobs In Atlanta
- *Snippet:* ... Chief Sales Officer»Chief Sales Officer, Atlanta. Chief ... tech startups and innovation centers. This ... CSO Recruitment at Cast USA. Do you have the ...

**2. Score: 6/10**  — [https://www.linkedin.com/in/calvin-allen-71951121](https://www.linkedin.com/in/calvin-allen-71951121)

- *Title:* Calvin Allen - Chief Strategy Officer CSO | Co-Founder
- *Snippet:* Chief Strategy Officer CSO | Co-Founder | Amazon Alum | 15+Yrs Enterprise Sales and Strategy | Partnerships | Fintech | Tech Startups ... Your California Privacy ...Read more

**3. Score: 3/10**  — [https://www.chiefoutsiders.com/news/cso-howard-doherty](https://www.chiefoutsiders.com/news/cso-howard-doherty)

- *Title:* Senior Technology Sales Executive to Take ...
- *Snippet:* ... CSO ... California in Los Angeles, California. About Chief Outsiders. Chief ...Read more

**4. Score: 1/10**  — [https://wellfound.com/role/r/chief-strategy-officer](https://wellfound.com/role/r/chief-strategy-officer)

- *Title:* Remote Chief Strategy Officer (CSO) Jobs in 2026
- *Snippet:* Head of / Director of Sales, USAFull-time. Remote • Austin. 7 days ago. 7 ... Tech Startups · Remote. For Recruiters. Overview · Recruit Pro · Curated ...Read more

**5. Score: 2/10**  — [https://trellis.net/list/climate-tech-startups-to-watch-in-2026/](https://trellis.net/list/climate-tech-startups-to-watch-in-2026/)

- *Title:* 15 Climate tech startups to watch in 2026
- *Snippet:* 15 Climate Tech Startups to Watch in 2026. These promising early-stage startups are innovating in three burgeoning sectors: data centers, materials and climate ...Read more

---

## Summary

- **Total variants:** 13
- **Total candidates judged:** 65 / 65
- **Failed judge calls:** 0
- **Overall mean score:** **3.46/10**

### Aggregate by expansion category (best → worst)

| Rank | Category | Variants | Category mean | Best variant mean | Total sum |
|---|---|---|---|---|---|
| 1 | `geography_broadening` | 3 | **4.8/10** | 6.0/10 | 72 |
| 2 | `verbatim` | 1 | **3.8/10** | 3.8/10 | 19 |
| 3 | `industry_broadening` | 3 | **3.47/10** | 5.6/10 | 52 |
| 4 | `title_broadening` | 3 | **3.33/10** | 4.8/10 | 50 |
| 5 | `combined_broadening` | 3 | **2.13/10** | 2.6/10 | 32 |

**Best expansion category:** `geography_broadening` (4.8/10 mean across 3 variant(s))

**Worst expansion category:** `combined_broadening` (2.13/10 mean across 3 variant(s))

### Top variants overall

| Rank | Mean | Max | Sum | Seed(s) | Query |
|---|---|---|---|---|---|
| 1 | **6.0/10** | — | 30 | `geography_broadening` | ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" "North America" |
| 2 | **5.6/10** | — | 28 | `industry_broadening` | ("VP Sales" OR "Head of Sales") "tech startups" "United States" |
| 3 | **5.0/10** | — | 25 | `geography_broadening` | ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" ("California" OR "New Yo... |
| 4 | **4.8/10** | — | 24 | `title_broadening` | ("VP Sales" OR "Vice President of Sales" OR "Sales VP") "cybersecurity SaaS" ... |
| 5 | **3.8/10** | — | 19 | `verbatim` | VP Sales or Head of Sales at US cybersecurity SaaS startups in the United States |
| 6 | **3.8/10** | — | 19 | `title_broadening` | ("Head of Sales" OR "Sales Director" OR "Sales Leader") "cybersecurity SaaS" ... |
| 7 | **3.4/10** | — | 17 | `geography_broadening` | ("VP Sales" OR "Head of Sales") "cybersecurity SaaS" ("USA" OR "US") |
| 8 | **3.2/10** | — | 16 | `industry_broadening` | ("VP Sales" OR "Head of Sales") "cybersecurity" "United States" |
| 9 | **2.6/10** | — | 13 | `combined_broadening` | ("Chief Sales Officer" OR "CSO") "tech startups" ("USA" OR "California") |
| 10 | **2.0/10** | — | 10 | `combined_broadening` | ("VP Sales" OR "Sales Director") "cybersecurity" ("USA" OR "North America") |
| 11 | **1.8/10** | — | 9 | `combined_broadening` | ("Head of Sales" OR "Sales Executive") "SaaS" "United States" |
| 12 | **1.6/10** | — | 8 | `industry_broadening` | ("VP Sales" OR "Head of Sales") "SaaS" "United States" |
| 13 | **1.4/10** | — | 7 | `title_broadening` | ("Chief Sales Officer" OR "CSO" OR "Sales Executive") "cybersecurity SaaS" "U... |
