# Documentation archive: provenance and relocation

**Cleanup 2026-11-14** consolidates only active instructions. It does **not**
erase the earlier scientific discussion. Every former root or active docs
Markdown file (except the overwritten canonical entrypoints) was copied
**byte-identically** to `docs/archive/2026-11-12-snapshot/`, with its original
relative name/path. The full mapping plus source-content hashes is in
[`2026-11-12-snapshot/RELOCATION_MAP.json`](archive/2026-11-12-snapshot/RELOCATION_MAP.json).
The snapshots of the three overwritten README/AGENTS entrypoints are also
kept there. Existing `docs/history/` and `docs/evidence/` remain unchanged.

| Former category | New location | Typical contents |
| --- | --- | --- |
| Root `IMPLEMENTATION_REPORT.md`, `SPARSE_README.md`, `*.txt` and historical `*_MANIFEST.json` | `docs/archive/2026-11-12-snapshot/<original-file>` | Historical install/validation claims; no longer root instructions |
| Root `docs/ALGORITHM_NOTES.md`, `LOCKED_EXPERIMENTS.md`, `CHAT_HANDOFF.md`, `RUN_REGISTRY.md`, etc. | `docs/archive/2026-11-12-snapshot/docs/<original-file>` | Complete earlier algorithm notes, run references, stage decisions |
| `docs/wireless/*.md` | `docs/archive/2026-11-12-snapshot/docs/wireless/` | Implementation plan, old runbook/validation/status, sensitivity review |
| `docs/wireless/{preimplementation,evidence,r150_joint_20261110}` | same folders under `docs/archive/2026-11-12-snapshot/docs/wireless/` | Detailed proposal audit, saved images/tables, joint-R150 raw review |
| Non-imported source `*.before_*` | `docs/archive/2026-11-12-snapshot/scratch_source/src/` | Old scratch snapshots; not importable live package files |
| `docs/history/`, `docs/evidence/` | **Remain in place** | Earlier independent date-stamped source history and audits |
| `docs/wireless/proposal/*.tex` | **Remain in place** | Primary wireless-design formula sources |

**Explicitly removed from the cleaned working repository:**
`backups/` (three old code backups) and `modified_source/` (three prior scratch
source files). They were **not silently imported or merged** into live
`src/`. Their relative names and SHA-256 digests are in the cleanup manifest
provided alongside the release, and original bytes remain recoverable from
the user's original uploaded `bayesfl.zip`. The old `reports/` paper text
was relocated to `reports/legacy/` rather than deleted.

`docs/EXPERIMENT_REGISTRY.json` is **still at its original path** because
baseline checkers and study generators load it. Historical root `.json`/`.txt` manifests are preserved in the dated archive
rather than left at the repository root. Runtime code does not import them;
the legacy source exporter includes those archived copies. The
first-submission and wireless learner source is not rewritten.

## What is authoritative now?

Use [`README.md`](README.md) for current documents and
[`RESULTS.md`](RESULTS.md) for historical results with explicit evidence
scope. Archived dates, "next step" notes and provisional instructions are
historical statements, not evidence that work was never completed later.

## Direct historical links

- [Selected paper profile (original)](archive/2026-11-12-snapshot/docs/LOCKED_EXPERIMENTS.md)
- [FOLA and KL source notes (original)](archive/2026-11-12-snapshot/docs/ALGORITHM_NOTES.md)
- [Prior chat handoff (original)](archive/2026-11-12-snapshot/docs/CHAT_HANDOFF.md)
- [Wireless original implementation notes](archive/2026-11-12-snapshot/docs/wireless/IMPLEMENTATION.md)
- [Joint R150 sensitivity full audit write-up](archive/2026-11-12-snapshot/docs/wireless/JOINT_CIFAR10_SENSITIVITY_R150_20261112.md)
- [Joint R150 review plots and tables](archive/2026-11-12-snapshot/docs/wireless/r150_joint_20261110/)
