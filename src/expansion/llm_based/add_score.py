"""Read a minimal4 report, run the LLM judge per SERP candidate, write a scored JSON.

This decouples the SERP step (which costs Bright Data quota) from the
judge step (which costs OpenAI tokens). Run minimal4 once → save the
report → run add_score.py against the saved report any number of times
with different judge models / prompts.

Input:  a JSON file produced by minimal4.py (with `variants[].serp_results`).
Output: a NEW JSON file at <input>_scored.json (path is configurable).

The output mirrors the input but:
- every `serp_results[i].llm_judge_result` is populated with a real
  LLMJudgeResult (instead of null);
- each variant gains a `scoring` block (mean / sum / per-candidate scores);
- the top-level report gains a `judging` block (run-level aggregate).

Run:
    python src/expansion/llm_based/add_score.py outputs/minimal4_<UTC>.json
    python src/expansion/llm_based/add_score.py outputs/minimal4_<UTC>.json --output outputs/scored.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---- sys.path bootstrap (same shape as minimal4.py) ----

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SDK_SRC = Path("/Users/ns/Desktop/projects/sdk-python/src")

for _path in (PROJECT_ROOT, SDK_SRC):
    p = str(_path)
    if p not in sys.path:
        sys.path.insert(0, p)


from dotenv import load_dotenv  # noqa: E402

from judge_logic import request_judge_verdict  # noqa: E402
from schemas import LLMJudgeResult  # noqa: E402


load_dotenv()


# ---- Logging ----

DEBUG = True


def _log_debug(message: str) -> None:
    if DEBUG:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        print(f"  [debug {ts}] {message}", flush=True)


def _log_warn(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"  [WARN  {ts}] {message}", flush=True)


# ---- Scoring ----

def _per_variant_scoring(per_candidate_scores: List[int]) -> Dict[str, Any]:
    n = len(per_candidate_scores)
    total = sum(per_candidate_scores)
    return {
        "candidate_count": n,
        "scores_per_candidate": per_candidate_scores,
        "sum_total_point": total,
        "mean_total_point": round(total / n, 2) if n else 0.0,
        "max_total_point": max(per_candidate_scores) if n else 0,
        "min_total_point": min(per_candidate_scores) if n else 0,
    }


def _ranking_summary(variants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build a compact ranking of variants by mean score for the run summary."""
    rows = []
    for v_idx, v in enumerate(variants):
        scoring = v.get("scoring") or {}
        rows.append(
            {
                "index": v_idx,
                "seeds": v.get("seeds", []),
                "query": v.get("query", ""),
                "candidate_count": scoring.get("candidate_count", 0),
                "mean_total_point": scoring.get("mean_total_point", 0.0),
                "sum_total_point": scoring.get("sum_total_point", 0),
            }
        )
    rows.sort(key=lambda r: r["mean_total_point"], reverse=True)
    return rows


def score_report(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """Read a minimal4 report, attach judge results + scoring, write to a new file."""

    report: Dict[str, Any] = json.loads(input_path.read_text(encoding="utf-8"))

    original_query: str = report["query_spec"]["natural_query"]
    variants: List[Dict[str, Any]] = report.get("variants", [])

    _log_debug(f"Loaded {len(variants)} variants from {input_path.name}")
    _log_debug(f"Original query: {original_query!r}")

    started_at = datetime.now(timezone.utc)
    total_candidates = 0
    judged_count = 0
    failed_count = 0

    for v_idx, variant in enumerate(variants, 1):
        seeds = variant.get("seeds", [])
        serp_results: List[Dict[str, Any]] = variant.get("serp_results", [])
        total_candidates += len(serp_results)

        print(f"\n[{v_idx}/{len(variants)}] seeds={seeds}  candidates={len(serp_results)}")

        variant_scores: List[int] = []

        for c_idx, serp_result in enumerate(serp_results, 1):
            link: str = serp_result.get("link", "") or ""
            metadata: Dict[str, Any] = serp_result.get("metadata") or {}
            title: Optional[str] = metadata.get("title")
            snippet: Optional[str] = serp_result.get("snippet")

            _log_debug(f"  judging [{c_idx}/{len(serp_results)}]: {link[:80]}")

            try:
                verdict: LLMJudgeResult = request_judge_verdict(
                    original_query=original_query,
                    link=link,
                    title=title,
                    snippet=snippet,
                )
            except Exception as exc:
                _log_warn(f"Judge failed for {link[:80]}: {exc}")
                serp_result["llm_judge_result"] = None
                failed_count += 1
                continue

            serp_result["llm_judge_result"] = verdict.model_dump(mode="json")
            variant_scores.append(verdict.total_point)
            judged_count += 1
            print(f"    [{c_idx}/{len(serp_results)}] score={verdict.total_point:2d}/10  {link[:80]}")

        variant["scoring"] = _per_variant_scoring(variant_scores)
        if variant_scores:
            print(
                f"  -> variant mean: {variant['scoring']['mean_total_point']:.2f}/10  "
                f"max: {variant['scoring']['max_total_point']}  "
                f"sum: {variant['scoring']['sum_total_point']}"
            )

    completed_at = datetime.now(timezone.utc)

    # Run-level aggregate across all candidates.
    all_scores: List[int] = []
    for variant in variants:
        all_scores.extend(variant.get("scoring", {}).get("scores_per_candidate", []))

    overall_mean = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0

    report["judging"] = {
        "source_report": str(input_path),
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "elapsed_seconds": round((completed_at - started_at).total_seconds(), 2),
        "total_candidates": total_candidates,
        "judged_count": judged_count,
        "failed_count": failed_count,
        "overall_mean_total_point": overall_mean,
        "variant_ranking": _ranking_summary(variants),
    }

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_scored.json"

    payload = json.dumps(report, indent=2, default=str)
    output_path.write_text(payload, encoding="utf-8")
    _log_debug(f"Wrote {len(payload):,} bytes to {output_path}")

    print()
    print("=== Done ===")
    print(f"Candidates judged:  {judged_count}/{total_candidates}")
    print(f"Failed:             {failed_count}")
    print(f"Overall mean score: {overall_mean}/10")
    print(f"Scored report:      {output_path}")

    return output_path


# ---- __main__ ----

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add LLM judge scores to a minimal4 SERP report."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the minimal4 JSON report (the one with variants[].serp_results).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path. Defaults to <input>_scored.json next to the input file.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(2)

    score_report(args.input, args.output)


if __name__ == "__main__":
    main()
