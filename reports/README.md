# `reports/` — the review-facing evidence interface

**Workflow:** [`docs/WORKFLOW.md`](../docs/WORKFLOW.md) defines the
researcher-controlled LAUNCH / MONITOR / EXTRACT process.
[`docs/TASK_TEMPLATE.md`](../docs/TASK_TEMPLATE.md) describes what a
preparation/verification task must return. A new Codex conversation reads
[`docs/PROJECT_STATUS.md`](../docs/PROJECT_STATUS.md) before interpreting
reports; this folder is review evidence, not live process state.

**Purpose:** This folder is the single, predictable location for compact,
reproducible **experiment reports** used for research review and decisions.
It is intentionally separate from `outputs/`, which holds *raw training
runs, checkpoint arrays, full event ledgers and resumes*.

## Folder layout

```text
reports/
  README.md                   # this contract — tracked
  REPORT_TEMPLATE.md          # checklist for interpreting any study — tracked
  legacy/                     # old generated paper summaries — retained
  report_<UTC-timestamp>_<study>/
    RESEARCH_REPORT.md        # concise evidence summary and diagnostic cautions
    RESEARCH_REPORT.json      # machine-readable run/round summaries
    HANDOFF_HASHES.json       # SHA-256 and bytes for copied evidence
    research_bundle.zip       # small attachable copy, NOT a resume bundle
    evidence/<exact-run-id>/
      resolved_config.yaml
      run_summary.json
      wireless/protocol.json
      wireless/layout_manifest.json
      metrics/global_metrics.csv
      metrics/wireless_rounds.csv
      metrics/wireless_clients.csv
      ... (other explicitly permitted metadata)
```

The writer **never** copies raw weights, checkpoints, `wireless/events.jsonl`,
whole datasets, private client data or partition NPZs. It does not smooth
accuracy, choose a best-test checkpoint as a substitute for the terminal
round, or infer missing results. New reports are immutable snapshot
artifacts, with a unique run study identity and hashes.

## Generate a report from a completed wireless run

From the repository root, with `PYTHONPATH="$PWD/src"` and the intended
Python interpreter:

```bash
# Read-only inspection; creates nothing.
python scripts/export_research_report.py \
  --run-dir outputs/EXACT_COMPLETED_WIRELESS_RUN

# Create a NEW uniquely named reports/report_.../ with readable and raw evidence.
python scripts/export_research_report.py \
  --run-dir outputs/EXACT_COMPLETED_WIRELESS_RUN \
  --write-report --report-name reference_cifar_r150

# Comparison report: explicit, matched studies; never choose 'latest' implicitly.
python scripts/export_research_report.py \
  --run-dir outputs/EXACT_RUN_A \
  --run-dir outputs/EXACT_RUN_B \
  --write-report --report-name resource_sweep
```

The newly created directory is printed on successful completion. The primary
file to review is `RESEARCH_REPORT.md`, accompanied by `RESEARCH_REPORT.json`
and exact `evidence/` CSVs. For sharing externally, use its
`research_bundle.zip`. **This ZIP cannot resume training.** It preserves the
saved metric/config evidence only. Reports do not create new training results.

### Integrity modes

- **Default strict**: demands a completed evaluated run and matching *raw
  byte* checkpoint/ledger hashes and metric accounting. Never labels an
  inconsistent archive clean.
- **`--records-only`**: explicit downgrade for archived copies whose
  checkpoint/ledger bytes have been transformed (e.g., CRLF). It still
  verifies recorded counts/bytes, client normalization and weighted KL, but
  marks integrity `records_only_unverified_checkpoint`. It must **never** be
  represented as a verified resumable checkpoint.

**No report export should rewrite source evidence.** Only a new `reports/`
subdirectory is created. If a run is incomplete/failed or has mismatched
client accounting, stop and inspect raw `outputs/` rather than forcing an
apparently complete report. Never edit the original CSV to fit an expected
narrative.

## Required analysis contents

A review report should include the fields from
[`REPORT_TEMPLATE.md`](REPORT_TEMPLATE.md): research question, exact source
runs, dataset/partition/seed, model/training method, selector and allocator,
physical scenario, comparability caveats, accuracy/NLL vs rounds and modeled
time, retention per client, **normalized** discarded KL, packet/control
bytes, allocation status and price-query counts, largest learning drops,
integrity status, and **next questions** rather than unproven explanations.

Legacy/nonwireless runs currently use `docs/tools/export_handoff.py` and
existing summary scripts; their reports can follow the same template, but
**do not** claim the wireless report exporter supports legacy v1 or BBB.

## Version control policy

Generated `reports/report_*/` directories are ignored by `.gitignore` by
default; commit only the *format contract* and reviewed small summary
artifacts if necessary. Never dump giant run outputs into `reports/`.
