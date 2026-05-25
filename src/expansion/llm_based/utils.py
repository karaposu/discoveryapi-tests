"""Shared utilities for the LLM-based expansion pipeline.

Two concerns live here:

  Logging
      log_debug(message), log_warn(message)
      DEBUG-gated debug prints + always-on warnings. Set
      `utils.DEBUG = False` to silence debug across all callers.

  Report I/O
      save_report(report, prefix, output_dir=None)
      Writes a report dict as JSON to <output_dir>/<prefix>_<run_id>.json.
      `prefix` lets each entry-point script tag its own output.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# ---- Logging ----
#
# DEBUG controls verbose per-call logging. Warnings always print.

DEBUG = True


def log_debug(message: str) -> None:
    if DEBUG:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        print(f"  [debug {ts}] {message}", flush=True)


def log_warn(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"  [WARN  {ts}] {message}", flush=True)


# ---- Report I/O ----

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"


def save_report(
    report: Dict[str, Any],
    prefix: str,
    output_dir: Optional[Path] = None,
) -> Path:
    """Write `report` as JSON to <output_dir>/<prefix>_<run_id>.json.

    `report` must contain a 'run_id' key. `output_dir` defaults to
    <project_root>/outputs and is created if missing.
    """
    target_dir = output_dir or DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{prefix}_{report['run_id']}.json"
    payload = json.dumps(report, indent=2, default=str)
    path.write_text(payload, encoding="utf-8")
    log_debug(f"Wrote {len(payload):,} bytes to {path}")
    return path
