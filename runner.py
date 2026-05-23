"""Entry point for the B2B contact-data expansion + SERP evaluation run.

Configuration lives in `config.py`. Pipeline logic lives in `experiment.py`.
"""

from __future__ import annotations

from dotenv import load_dotenv

from experiment import run, save_report

load_dotenv()


def main() -> int:
    report = run()
    output_path = save_report(report)
    print(f"Report saved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
