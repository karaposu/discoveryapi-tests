# How the expansion benchmark *should* be structured

## What we have today (and why it's wrong for Task 1)

The runner currently defines 5 "maximalist" combinations in `config.py:160`. Each one is a densely-specified bundle that mixes **all** of the following at once:

- a `site:` operator (from `source_lane`),
- OR-broadening of role titles,
- quoted industry / geography phrases,
- a long list of negative terms.

When SERP / judge scores differ between two of these combinations, **we cannot tell which factor caused the difference**. We only know "this stack scored better than that stack." That answer is useless for Task 1, whose explicit goal is to *find which expansion prompt produces the best downstream SERP results*. To answer that, we have to test factors in isolation, not stacks against stacks.

## The principle: ablation, not stack-vs-stack

Treat each transformation as a single factor and test the **marginal contribution** of each one. The minimum viable comparison is:

| Combination | `site:` | OR-title | quoted | negatives |
|---|:-:|:-:|:-:|:-:|
| baseline (raw query) | — | — | — | — |
| +site only | ✓ | — | — | — |
| +or only | — | ✓ | — | — |
| +quoted only | — | — | ✓ | — |
| +negatives only | — | — | — | ✓ |
| +site +negatives | ✓ | — | — | ✓ |
| +all | ✓ | ✓ | ✓ | ✓ |

With this layout each row pair answers one question:

- `baseline` vs `+site` → does the `site:` operator help on its own?
- `baseline` vs `+negatives` → do negatives help on their own?
- `+site` vs `+site +negatives` → do negatives still help once `site:` is in place?
- `+negatives` vs `+site +negatives` → does `site:` still help once negatives are in place?
- `+all` vs anything → does piling everything on actually outperform a leaner combo, or does it hit diminishing returns?

That is the kind of signal Task 1 was set up to produce.

## Two factor families: heuristic and LLM-driven

Heuristic-only ablation isn't enough for this benchmark. The whole reason to expand a query semantically is to handle terminology variation that no hardcoded list will cover. So we keep **both** layers and treat them as separate factor families that compose.

### Heuristic factors (deterministic, attribution-clean)

These are pure Python string transformations. Same input → same output, every run. No LLM creativity in the loop.

- `heur_site` — prepend a `site:` operator chosen by the combination (e.g. `site:linkedin.com/in`).
- `heur_negatives` — append a short list of negative terms (e.g. `-jobs -hiring`).
- `heur_quoted_phrases` — wrap industry / geography in double quotes.
- `heur_or_title` — wrap a fixed title list in `("VP Sales" OR "Head of Sales")`.

Each heuristic is a single, well-defined transformation. The atoms (which negatives, which title list, which site target) live in `config.py` and never change inside a run.

### LLM factors (semantic broadening)

These ask the LLM for semantic alternatives that a hardcoded list could never anticipate.

- `llm_title_broadening` — LLM proposes role-title synonyms (`"VP Sales"` → `"CRO"`, `"Head of Revenue"`, `"VP Revenue"` …).
- `llm_industry_broadening` — LLM proposes industry synonyms (`"cybersecurity SaaS"` → `"security software"`, `"infosec platform"` …).
- `llm_seniority_broadening` — LLM proposes seniority-level rewrites where appropriate.

LLM factors are evaluated **once per run**: a single call up front produces an `Atoms` object holding every semantic list we might need. Every combination then renders its query deterministically from `(atoms, factors)`. This matters because it makes the comparison fair — when two combos both use `llm_title_broadening`, they get *exactly the same broadened title list*, so any score difference between them is attributable to the *other* factors, not to the LLM's run-to-run variance.

### How heuristic and LLM factors compose

A combination is just a set of flags across both families. The renderer is deterministic given the atoms:

```
render_query(factors, atoms, original_query)
```

The LLM never writes a final query. It only produces atoms. Python assembles the final query. This way the LLM contributes semantic content but cannot quietly add or drop a term that contaminates the experiment.

## Combination logic: every meaningful pair must be tested

The combination list exists to **isolate marginal contributions** and **find the strongest pairs**. The rule is:

1. **Include the baseline.** Without it, "improvement" has no zero point.
2. **Include every single factor in isolation.** This gives the per-factor contribution.
3. **Include every two-factor pair.** This is where the most useful signal lives — most real-world improvement comes from a small interaction (e.g. `site:` only helps when `negatives` are also present, or `llm_title` only helps when `quoted_phrases` lock the industry).
4. **Include the everything-on combination.** This sets the upper bound and lets us see diminishing returns vs. the lean combos.
5. **Optionally include three-factor combinations** that the pair signals suggest are interesting.

Skipping any of (1) through (4) leaves a hole in the analysis. Skipping the baseline means we can't show the expansion is even net-positive. Skipping isolation rows means we can't attribute. Skipping pairs means we miss interaction effects, which is exactly what Task 1 is meant to surface.

## The full ablation matrix

This is the set the runner should enumerate by default. Heuristic factors are abbreviated `H_*`, LLM factors `L_*`.

| label | H_site | H_neg | H_quoted | H_or | L_title | L_industry |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| baseline                     | — | — | — | — | — | — |
| H_site                       | ✓ | — | — | — | — | — |
| H_neg                        | — | ✓ | — | — | — | — |
| H_quoted                     | — | — | ✓ | — | — | — |
| H_or                         | — | — | — | ✓ | — | — |
| L_title                      | — | — | — | — | ✓ | — |
| L_industry                   | — | — | — | — | — | ✓ |
| H_site + H_neg               | ✓ | ✓ | — | — | — | — |
| H_site + H_quoted            | ✓ | — | ✓ | — | — | — |
| H_site + H_or                | ✓ | — | — | ✓ | — | — |
| H_site + L_title             | ✓ | — | — | — | ✓ | — |
| H_site + L_industry          | ✓ | — | — | — | — | ✓ |
| H_neg + H_quoted             | — | ✓ | ✓ | — | — | — |
| H_neg + L_title              | — | ✓ | — | — | ✓ | — |
| H_or + L_title               | — | — | — | ✓ | ✓ | — |
| L_title + L_industry         | — | — | — | — | ✓ | ✓ |
| H_all (all heuristics)       | ✓ | ✓ | ✓ | ✓ | — | — |
| L_all (all LLM)              | — | — | — | — | ✓ | ✓ |
| H_all + L_all                | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Nineteen combinations. Every one must be tested — the matrix is the experiment.

## What each pairwise comparison teaches

Read the report as a matrix of differences, not as a leaderboard.

- **baseline → H_***: marginal value of each heuristic on its own.
- **baseline → L_***: marginal value of each LLM-driven broadening on its own.
- **H_* → H_* + H_***: does heuristic A still help once heuristic B is in place? Reveals dependency / redundancy between heuristics.
- **H_* → H_* + L_***: does LLM broadening contribute *on top of* a heuristic? Reveals whether the LLM is doing real semantic work or just paraphrasing.
- **L_* → L_* + L_***: do two LLM-driven factors interact? Sometimes broadening titles AND broadening industry overshoots and dilutes precision.
- **H_all vs H_all + L_all**: does the LLM add anything once every heuristic is on, or has the heuristic stack saturated?
- **anything vs H_all + L_all**: lets us spot diminishing returns. If a 2-factor combo beats the everything-on combo, the everything-on combo is too aggressive.

## Cost (rough order of magnitude)

For N combinations and `JUDGE_TOP_N = 5`:

| Stage | Calls |
|---|---|
| Atoms (one LLM call per run, regardless of N) | 1 |
| SERP | N |
| Judging | N × `JUDGE_TOP_N` |

For the 19-row default matrix: `1 + 19 + 95 = 115` external requests per run. That's the budget for one full ablation pass.

## Summary

- One factor per row, every row tested.
- Heuristic and LLM factors are **separate families that compose**, not alternatives.
- The LLM produces *atoms* once per run; Python deterministically assembles the final query strings.
- The report is read as a matrix of pairwise differences, not a leaderboard of stacks.
- The whole point is to identify the **most effective pairs**, not to find a single winning stack.
