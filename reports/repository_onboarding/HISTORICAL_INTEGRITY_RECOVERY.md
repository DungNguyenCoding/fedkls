# FedKLS — Historical Integrity Recovery

**Restored 86 archived documents and all 21 wireless metric CSVs through exact SHA-256-matched
newline conversion.** Document verification is now **90/91**, including four files already correct.
**All seven wireless runs pass strict report validation and the existing strict resume loader.**
One document remains unchanged and unresolved; therefore the full suite remains **216 passed, 1 failed**.
Wireless tests: **77 passed**. No tests were changed and no training was run.

Generated **2026-11-14T17:01:37+09:00**, Asia/Seoul.

## Repository state and authorization

- Repository: `/home/micl/DungNDH/fedkls`; Conda `dungndh`, Python 3.10.20.
- Base recovery commit: `4946bdc23bd0060105cc708897cd31306d279cba`.
- New branch: `fix/historical-evidence-newlines`.
- Initial tracked working tree and index were clean. The 75 existing untracked onboarding artifacts were preserved.
- The current brief explicitly authorizes LF/CRLF candidates in memory and restoration only on an exact recorded raw SHA-256 match. This narrowly scoped authorization governs the restorations below.
- No original full ZIP was used. No alternative text, encoding, spacing, numeric values, expected hash values or scientific settings were substituted.
- The final commit is the single commit containing this report; its exact SHA is supplied in the completion response and can be resolved with:

```bash
git log -1 --format=%H -- reports/repository_onboarding/HISTORICAL_INTEGRITY_RECOVERY.md
```

The previous [recovery report](RECOVERY_VERIFICATION.md), reproducibility rules, relocation manifest,
archived instructions and existing checkpoint/reporting validators were reviewed. Earlier reports retain
their original bytes and remain dated evidence; this report records the new verification state.

## Initial integrity and authenticated restoration method

| Evidence set | Initial state | Final state |
| --- | --- | --- |
| Archived relocation entries | 91 present; 4 raw hashes correct, 87 mismatching | 90 correct; 86 restored, 4 unchanged; 1 unresolved |
| Seven runs' metric CSVs | 21 mismatching | 21 restored and matching |
| Checkpoint state JSON, NPZ and event ledgers | Raw digests previously verified | Still match; bytes unchanged |
| Strict report/resume checks | All seven failed at committed metric hashes | All seven pass |

The authoritative document digests were read from the **unchanged**
`docs/archive/2026-11-12-snapshot/RELOCATION_MAP.json`. Metric digests were read from each run's existing
R150 checkpoint JSON `tracked_sha256` map, after verifying that JSON's own raw digest against `latest.json`.
No recorded digest values or authority records were rewritten.

For a mismatching file, the procedure required valid UTF-8 text without binary/control-byte content,
constructed these two candidates in memory, and hashed the candidate **raw bytes**:

```text
LF   = raw.replace(CRLF, LF).replace(bare_CR, LF)
CRLF = LF.replace(LF, CRLF)
```

A write was permitted only when **exactly one** candidate matched the recorded expected SHA-256.
All 107 restored files matched the **CRLF** candidate. Four already-correct PNG files were left untouched.
The one nonmatching text document was left untouched. This is digest-authenticated recovery relative to
the existing authorities, rather than a claim that normalized content is sufficient for strict integrity.

Before any write, the 107 eligible originals were copied outside the repository and their backup hashes
verified. Each replacement was written atomically, preserving file mode, and rehashed afterward.
The seven existing wireless writer locks were acquired without modifying lock files to exclude concurrent
writers during metric restoration. No large output directory was copied or force-added.

Backup location:

```text
/tmp/fedkls_historical_integrity_backup__pishz6i
```

The backup contains original pre-restoration bytes and `BACKUP_MANIFEST.json`; it is not committed.
All 107 backups were rehashed successfully after restoration.

Detailed before/candidate/expected/restored hashes, decisions, newline counts, backup locations and
Git tracking status are in [restoration_results.json](historical_integrity/restoration_results.json).
The compact complete list of restored paths and expected/restored SHA-256 values is
[restored_files.csv](historical_integrity/restored_files.csv). Planning evidence is retained in
[restoration_plan.json](historical_integrity/restoration_plan.json).

## Archived documents: 90 of 91 verified

The 86 authenticated text restorations include historical Markdown, text/CSV/JSON evidence and archived
source snapshots. Existing expected hashes and JSON field values were not changed; active source and
scientific configuration files were outside the restoration set. All 86 restored digests equal their
individual relocation-map references exactly.

The sole unresolved file is:

```text
docs/archive/2026-11-12-snapshot/docs/DOCUMENTATION_VALIDATION.md
```

| Digest | Raw SHA-256 |
| --- | --- |
| Expected by relocation manifest | `3ecf9ba6c65c5c3700a03134165a05c0f09fd2b52d5b7f3d66bce35524a70048` |
| Current / LF candidate / unchanged final | `c93b9ac8555a62d10bd3b37e69c799a7b440c78ddb94761bfe860f0f8470fd99` |
| CRLF candidate | `ca25ffef39bda7cb6741742bdf5c7cd89f4cfcbb66bf107794c4e5511dc2c536` |

Neither permitted candidate matches. Its initial and final bytes are identical. The evidence does not
establish which additional historical difference exists, and no further reconstruction or manifest edit
was attempted. Authenticated original bytes or separately authorized investigation are needed for this
one document. No claim of 91/91 integrity is made.

An independent post-restoration raw-byte pass confirms all 91 files are present and **90 hashes match**.
The existing archival test now reaches this unresolved entry; previously it stopped at archived `AGENTS.md`.
Full per-path verification is in [archive_verification.json](historical_integrity/archive_verification.json).

## All 21 wireless CSVs restored without metric changes

The exact affected files in each named run were:

- `metrics/global_metrics.csv`
- `metrics/wireless_clients.csv`
- `metrics/wireless_rounds.csv`

Every selected CRLF candidate matches its corresponding committed checkpoint digest. The procedure
compared parsed CSV records before/after **as strings**, including headers, row order, field order and
numeric spelling; every comparison is identical. It also compared bytes after removing only newline
convention differences. No floating-point conversion or numeric reserialization was used.

Thus recorded accuracy, NLL, retained counts, allocation diagnostics, byte totals and modeled resources
remain unchanged. CSV record digests and row counts are included in the restoration evidence. Restored
CSV bytes are the authenticated source bytes; derived report CSVs use LF for ordinary report formatting.

## Verification commands and test results

All commands ran from the repository root in `dungndh`, using
`/home/micl/anaconda3/envs/dungndh/bin/python`. Existing editable imports select this checkout.

| Command | Exit | Result | Measured wall s | Exact transcript |
| --- | ---: | --- | ---: | --- |
| `python -m pytest -q` | 1 | **216 passed, 1 failed**, 0 skipped | 62.851 | [pytest_full](historical_integrity/logs/pytest_full.transcript.json) |
| `python -m pytest -q tests/wireless` | 0 | **77 passed**, 0 skipped | 14.030 | [pytest_wireless](historical_integrity/logs/pytest_wireless.transcript.json) |
| `python -m pytest -q tests/test_repository_layout.py::test_relocated_historical_docs_are_byte_preserved` | 1 | 1 failed: unresolved document | 0.323 | [archive_test](historical_integrity/logs/archive_test.transcript.json) |
| `python docs/tools/export_handoff.py --check` | 0 | **24 endpoints and byte budgets verified** | 0.270 | [legacy_endpoints](historical_integrity/logs/legacy_endpoints.transcript.json) |

There are **no skips or collection errors** in the full or wireless suite. The only full-suite failure is
`tests/test_repository_layout.py::test_relocated_historical_docs_are_byte_preserved`, at line 31,
comparing the unresolved document's actual `c93b9ac8555a62d10bd3b37e69c799a7b440c78ddb94761bfe860f0f8470fd99` with expected `3ecf9ba6c65c5c3700a03134165a05c0f09fd2b52d5b7f3d66bce35524a70048`.
The dedicated archival test fails for that same reason. All failure details and exact emitted output
are retained in the linked transcript JSON files; extracting `stdout_utf8` reproduces the UTF-8 transcript
including whitespace. No traceback or test assertion was trimmed or weakened.

The full suite reports 13 upstream Matplotlib/Pyparsing deprecation warnings. Tests inherited
`PYTHONDONTWRITEBYTECODE=1` and `PYTEST_ADDOPTS='-p no:cacheprovider'`; only pytest cache storage was
disabled. No tests were filtered out of either requested suite. Measured command wall seconds above
are distinct from simulated wireless resource time.

The existing legacy checker again verifies **all 24 original benchmark endpoints and exact byte-budget
totals**. Recorded MNIST/CIFAR-10 configurations, results and the separate s5/B5 versus selected s10/B10
conditions remain unchanged. No accuracy was rerun through full training.

## Seven-run strict checkpoint and resume verification

Each run was inspected through the existing documented **strict** command:

```text
python scripts/export_research_report.py --run-dir <exact-run-directory>
```

All seven commands exit **0**. No `--records-only` fallback was used. The underlying strict analysis
reports `checkpoint_integrity.status=verified_byte_digests`, with no issues, and validates recorded
packet/accounting, all-client sample weighting, KL totals, completed evaluations and fixed-slot clocks.

| Run | Recorded metrics | State JSON | Arrays | Event ledger | Strict resume |
| --- | --- | --- | --- | --- | --- |
| Reference | Pass | Pass | Pass | Pass | Eligible |
| U170 | Pass | Pass | Pass | Pass | Eligible |
| U160 | Pass | Pass | Pass | Pass | Eligible |
| U150 | Pass | Pass | Pass | Pass | Eligible |
| B0550 | Pass | Pass | Pass | Pass | Eligible |
| B0750 | Pass | Pass | Pass | Pass | Eligible |
| B0950 | Pass | Pass | Pass | Pass | Eligible |

The resume check also invoked the **existing, unmodified `WirelessState(..., resume=True)` loader**
with the saved configuration, reconstructed model layout, actual canonical partition-content hash and
the configured channel/trace identity. It passed configuration fingerprint, protocol, partition, trace,
layout, raw checkpoint/metric/ledger hashes, restored array shapes/precisions, model snapshot and cap
checks for every run. The saved partition metadata agrees with the cached NPZ's canonical content hash.

Only in-memory state was restored for validation. No runner, local training, evaluation, checkpoint save,
finalize, metric append or actual continuation was invoked. The saved R150 caps yield `max_rounds`;
continuing training would require a separately authorized compatible cap extension and the same pinned
conditions. Eligibility here refers to the existing software's complete strict validation, not a new
training result or real-GPU execution test.

Exact run identities:

- **Reference**: `outputs/run_wireless_cifar_eqb_joint150_fixed_v1_cifar10_a0p01_f1_joint_seed0_20261109_230207`
- **U170**: `outputs/run_wireless_cifar_joint_u170_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_115923`
- **U160**: `outputs/run_wireless_cifar_joint_u160_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_171008`
- **U150**: `outputs/run_wireless_cifar_joint_u150_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_221432`
- **B0550**: `outputs/run_wireless_cifar_joint_b0550_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_115526`
- **B0750**: `outputs/run_wireless_cifar_joint_b0750_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_170448`
- **B0950**: `outputs/run_wireless_cifar_joint_b0950_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_221033`

All strict component statuses and run-level evidence hashes are in
[wireless_strict_checks.json](historical_integrity/wireless_strict_checks.json). Individual exact CLI
transcripts are `historical_integrity/logs/wireless_<label>_strict.transcript.json`; the combined read-only
loader verification is [strict_wireless_checks.transcript.json](historical_integrity/logs/strict_wireless_checks.transcript.json).
No additional checkpoint/state/ledger problem was discovered after metric-byte recovery.

## Git byte preservation and diff review

All **107 restored files were already tracked**. No ignored/untracked historical output was force-added.
Existing `.gitattributes` rules return **`text: unset`** for every restored path, as recorded in
[attributes.json](historical_integrity/attributes.json). The attributes and `.gitignore` remain unchanged.
For every restored tracked file, staged and committed blob SHA-256 values are checked against its
authoritative expected raw digest; accepting a normalized blob is not sufficient.

The full restoration diff is empty when ignoring end-of-line whitespace. Exact candidate hashes,
normalized-line equivalence and CSV/JSON field equality establish that differences are solely newline
bytes. Ordinary `git diff --check` reports **43,494 diagnostics in 107 restored paths**
because the authenticated CRLF bytes are treated as end-of-line whitespace. They are retained exactly.
A compact per-file diagnostic inventory is in
[historical_whitespace_checks.json](historical_integrity/historical_whitespace_checks.json).

The required `git diff --cached --check` is reviewed separately for authenticated restorations and the
new report artifacts. Historical-byte diagnostics are documented; new report/JSON/CSV files must pass
the scoped formatting check. No authenticated evidence is trimmed to satisfy a whitespace convention,
and no Git whitespace-suppression rule or integrity-test change is introduced. The staged blob and formatting results are in
[git_preservation_checks.json](historical_integrity/git_preservation_checks.json).

The final staged scope is limited to the 107 authenticated historical-byte restorations and this new
report/evidence. The unresolved document, active source, tests, configs, hash authorities, checkpoints,
event ledgers, previous reports and the 75 pre-existing untracked files are excluded from staging.
The final single commit uses `fix: restore verified historical evidence bytes`; no push is performed.

## Protected-state checks and readiness

The preservation audit verifies:

- **1,504 protected non-target files** unchanged, including all 55 active source files and 936 files under `scripts/configs/`.
- All **150 prior report artifacts** unchanged; all 75 pre-existing untracked files retained.
- All **26,020 nonselected output files** unchanged, including checkpoint JSON/NPZ files, event ledgers, partitions and other experiments.
- All 107 backups verified; the four already-correct documents and one unresolved document left unchanged.
- No active algorithm, model, partition, optimizer, seed, schedule, clipping, communication budget, protocol, scientific setting, test or expected hash value modified.

The nonselected-output raw-byte tree digest is identical before/after:

```text
80b670b1e59b890053f4f5eb2c4c6fb9259e2c7e1cc10cd411979fd43d3c041e
```

The tree fingerprint hashes sorted relative paths plus each raw file SHA-256; it excludes only the
21 explicitly authorized metric targets. Details are in
[preservation_checks.json](historical_integrity/preservation_checks.json) and the before-state inventory
[baseline.json](historical_integrity/baseline.json).

**Remaining issue:** one archived document lacks a hash-matching LF/CRLF candidate, so archival
preservation remains 90/91 and the full test gate remains red. Earlier unrelated `flwr-baselines`
dependency conflicts remain as recorded in the previous recovery report; dependency maintenance and
real Ray/CUDA training were outside this task and were not newly certified here.

**Readiness:** source development can proceed with the disclosed archival gate. All seven audited R150
wireless checkpoints now satisfy the existing strict resume-integrity checks under their saved conditions.
No training, additional historical guessing, algorithm work or automatic push follows this verification.
