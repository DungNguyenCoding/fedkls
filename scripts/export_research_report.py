#!/usr/bin/env python3
"""Read completed wireless runs and optionally create a report under reports/.

No training, metric modification, checkpoint repair or resume operations.
Default is a read-only terminal summary; --write-report creates a new directory.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bayesfl.wireless.research_report import analyze_run, export_directory


def report_name(requested: str | None, runs: list[Path]) -> str:
    if requested is not None:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}", requested):
            raise ValueError("--report-name must be a simple 1..100-character ASCII label")
        suffix = requested
    elif len(runs) == 1:
        suffix = re.sub(r"[^a-zA-Z0-9_.-]", "_", runs[0].name)[:65]
    else:
        suffix = "comparison_" + str(len(runs)) + "runs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f_utc")
    return f"report_{stamp}_{suffix}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, action="append", required=True,
                        help="Exact completed wireless directory; repeat for comparison")
    parser.add_argument("--write-report", action="store_true",
                        help="Write a new reports/report_<timestamp>_<name>/ directory")
    parser.add_argument("--report-name", type=str,
                        help="Short optional report label (requires --write-report)")
    parser.add_argument("--records-only", action="store_true",
                        help="EXPLICIT downgrade for byte-altered archive copies; verify recorded metrics "
                             "but mark checkpoint/ledger integrity unverified, never resumable")
    args = parser.parse_args()
    if args.report_name is not None and not args.write_report:
        parser.error("--report-name requires --write-report")
    try:
        runs = [p.expanduser().resolve(strict=True) for p in args.run_dir]
        if args.write_report:
            target = ROOT / "reports" / report_name(args.report_name, runs)
            records = export_directory(runs, target, records_only=args.records_only,
                                       repository_root=ROOT)
        else:
            target = None
            records = [analyze_run(path, records_only=args.records_only) for path in runs]
        for r in records:
            print(f"{r['run']}: R{r['completed_rounds']}, accuracy={r['final_accuracy_percent']:.3f}%, "
                  f"keep={100*r['final_mean_keep_ratio']:.2f}%, "
                  f"modeled_time={r['cumulative_modeled_time_seconds']:.3f}s; "
                  f"checkpoint={r['checkpoint_integrity']['status']} "
                  f"scope={r['validation_scope']}")
        if target:
            print(f"NEW REPORT: {target}")
            print(f"PORTABLE BUNDLE: {target/'research_bundle.zip'}")
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
