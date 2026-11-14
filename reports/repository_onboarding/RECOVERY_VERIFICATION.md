# FedKLS — Recovery Verification

**Source/environment recovery is verified; archival restoration remains pending.** All source modules
import from the current checkout. The full suite has **216 passed, 1 failed, 0 skipped, 0 collection errors**;
the wireless suite has **77 passed, 0 failed, 0 skipped**. The sole test failure is the existing historical
document-byte mismatch. **None of the seven audited wireless checkpoints is verified safe to resume.**

Generated **2026-11-14T16:31:52+09:00** (Asia/Seoul). This is an engineering verification of existing source and recorded
results. No full MNIST/CIFAR-10 training, scientific redesign, checkpoint rewrite, or historical-byte
reconstruction was performed.

## 1. Repository state and commit scope

| Field | Verified state |
| --- | --- |
| Working directory | `/home/micl/DungNDH/fedkls` |
| Starting branch / base commit | `main` / `61c60a027fe75404fc6275d0eaf85f7c116d7837` |
| Recovery branch | `fix/repository-integrity`, newly created |
| Initial working tree | Tracked files and index clean; 75 files from the previous onboarding report were already untracked and were preserved. |
| Final commit | The single recovery commit containing this report on `fix/repository-integrity`; resolve its exact SHA with the command below. The completion response also supplies the SHA. |
| Allowed commit contents | New `.gitattributes`, this report, and new `recovery/` verification evidence/logs only. Previous onboarding artifacts are not included. |

```bash
git log -1 --format=%H -- reports/repository_onboarding/RECOVERY_VERIFICATION.md
```

The researcher restored the four data modules before this task in the base commit. They were not
restored a second time. No source, `.gitignore`, experiment config, test, or existing report was edited.
No automatic push is part of this recovery.

The root research invariants, current reproducibility/reporting contracts and
[initial verification](INITIAL_VERIFICATION.md) were reviewed. New evidence is isolated under
`reports/repository_onboarding/recovery/` to preserve the previous report and its logs.

## 2. Environment and import identity

Every command ran after explicit activation of Conda `dungndh` from the repository root. Before repair,
the editable installation resolved to `/home/micl/DungNDH/micl/bayesfl`. The following authorized install
completed with exit 0, using existing build tools and no dependency resolution or package index:

```bash
source /home/micl/anaconda3/etc/profile.d/conda.sh
conda activate dungndh
python -m pip install -e . --no-deps --no-build-isolation --no-index
```

Without any `PYTHONPATH` override, `bayesfl.__file__` now resolves to
**`/home/micl/DungNDH/fedkls/src/bayesfl/__init__.py`**. Editable `direct_url.json` names this repository.
All **55** source modules, including the restored data package, import successfully from its `src/` tree.
`python -m bayesfl.main --help` also exits 0 for the current source.

| Component | Current value |
| --- | --- |
| Python / interpreter | 3.10.20 / `/home/micl/anaconda3/envs/dungndh/bin/python` |
| Conda prefix | `/home/micl/anaconda3/envs/dungndh` |
| pip | 26.1.2 |
| PyTorch / torchvision | 2.11.0+cu128 / 0.26.0+cu128 |
| Compiled CUDA / cuDNN | 12.8 / 91900 |
| Flower / Ray / Bayesian-Torch | 1.29.0 / 2.51.1 / 0.5.0 |
| NumPy / PyYAML / Matplotlib / pytest | 1.26.4 / 6.0.3 / 3.8.4 / 8.4.2 |
| Host GPUs | Two NVIDIA GeForce RTX 5090, 32,607 MiB each; driver 580.65.06 |
| Host CUDA discovery | `torch.cuda.is_available() == True`; device count 2; `nvidia-smi` exits 0 |

The sandbox cannot access NVIDIA device nodes: its CUDA probe returned false and `nvidia-smi` exited 9.
An approved read-only host probe in the **same Conda environment** verified the GPUs. Tests ran in the
sandbox; no real Ray/CUDA training workload or GPU kernel test was run.

All direct FedKLS dependency constraints and all **20 applicable Flower simulation dependencies** are
satisfied. `pip check` still exits **1** for the separately installed `flwr-baselines 1.0.0`:

| Requirement from `flwr-baselines` | Installed |
| --- | --- |
| `pandas>=1.5.3,<2.0.0` | 2.2.2 |
| `pillow==10.2.0` | 12.1.1 |
| `torch==2.4.1` | 2.11.0+cu128 |
| `torchvision==0.19.1` | 0.26.0+cu128 |

That package is not a declared FedKLS dependency. The conflicts were diagnosed and left unchanged;
PyTorch, CUDA, NumPy and unrelated packages were not upgraded/downgraded. Matplotlib/Fontconfig report
nonwritable user caches in the sandbox and use temporary storage where available. These diagnostics did
not cause test failures.

Evidence: [install log](recovery/logs/editable_install.log),
[import verification](recovery/logs/import_after_install.log), [CLI help](recovery/logs/cli_help.log),
[environment](recovery/environment.json), [host GPU discovery](recovery/gpu_host.json),
[Flower dependency checks](recovery/flower_simulation_dependencies.json),
[module origins](recovery/module_partition_checks.json).

## 3. Restored source integrity

All four files exist, are Git-tracked in base commit `61c60a02`, remain byte-identical to the recovery
intake snapshot, and import from the current repository:

| Data source | SHA-256 (intake = final) |
| --- | --- |
| `src/bayesfl/data/__init__.py` | `f6e47344a32fa93b5175bdb9fa22244fc37525df95b78fed1dc0ca664c920f0a` |
| `src/bayesfl/data/datasets.py` | `8c0356992fc61d931018b4bc490e1c2737c11c810cbb9a429c6995e6fb9010d5` |
| `src/bayesfl/data/partition.py` | `4f041d5901973ca04046e6dbc9023f9d52dcc414fcf9435dde29b2613ecfaa4b` |
| `src/bayesfl/data/transforms.py` | `315971b7b67f4c6eeee52002e66e59b236d92e27fec3500e1551b085b89851a1` |

The final protected-file audit checks **1,449 files**, including **55 source files** and
**936 experiment configurations**. It finds **zero byte changes**. `.gitignore` and all four
restored modules are unchanged. Source and experiment settings were not staged for the recovery commit.

The now-available canonical `_hash_partitions(load_partition(...))` implementation verifies both
selected seed-0 cached partitions against their saved logical content hashes:

| Selected partition NPZ | Canonical content SHA-256 | Result |
| --- | --- | --- |
| `mnist_fixed_labels_s10_c1_n20_seed0.npz` | `f083a94a732554c495b304d604222b3c68efc46237b56970f1c00f61f64f015a` | Verified |
| `cifar10_paper_dirichlet_a0.01_n20_seed0.npz` | `914fe035f7b504b0059ca85b5a6a194bd41027fb2cfe2765ee777142d68280f2` | Verified |

This closes the previous audit's partition-checksum limitation. Both datasets also open with
`download=False`: MNIST train/test **60,000/10,000**, CIFAR-10 train/test **50,000/10,000**.
No partition was regenerated and no dataset was downloaded.

Evidence: [module and partition checks](recovery/module_partition_checks.json),
[data accessibility](recovery/data_access.json), [preservation audit](recovery/final_preservation_checks.json).

## 4. Changes made and original-byte restoration status

There was no existing `.gitattributes`. The new file contains five narrowly scoped `-text` rules;
each has an explanatory comment:

| Rule | Purpose |
| --- | --- |
| `docs/archive/** -text` | Keep archived document bytes used by relocation/provenance SHA-256 records. |
| `docs/history/** -text` | Preserve earlier source/documentation snapshots and their provenance identities. |
| `docs/evidence/** -text` | Preserve original audit logs and source-inventory evidence with recorded hashes. |
| `outputs/** -text` | Preserve raw metrics, ledgers, checkpoint files and partition evidence used by byte-integrity checks. |
| `validation/** -text` | Preserve dated validation receipts and archive-identification evidence. |

`git check-attr` verifies `text: unset` for representatives of all five protected locations; source files
retain `text: unspecified`. Unrelated attributes were not overwritten. No `git add --renormalize`,
line-ending conversion, stored-hash update or formatting rewrite was performed. These rules prevent
future Git text conversion in the listed locations; they do not repair existing mismatches.

**Historical files restored: none. Restoration status: pending.**
`FedKLS_clean_refactor_full_with_results_v2.zip` was not available in the checked project/user-attachment
locations, home directory, Downloads/Desktop locations or top-level temporary directory. Other older
FedKLS ZIPs were found but were not substituted for the requested reference. No ZIP was extracted over
the working tree, and no unknown original bytes were inferred from stored hashes or reconstructed by
changing line endings. Exact search scope and results are in [archive availability](recovery/archive_availability.json).

Repository additions are limited to `.gitattributes`, `RECOVERY_VERIFICATION.md` and the new `recovery/`
evidence/logs. No large model files, raw arrays, complete training outputs or event-ledger copies were
added to reports. [Attribute check log](recovery/logs/attributes.log).

## 5. Full test results

```bash
python -m pytest -q
```

Exit **1**; **216 passed, 1 failed, 0 skipped, 0 collection errors; 13 warnings**. Measured command wall time **28.825 seconds**.

**The only failure** is
`tests/test_repository_layout.py::test_relocated_historical_docs_are_byte_preserved`.
It fails at `tests/test_repository_layout.py:31` while comparing the archived `AGENTS.md` to the saved
relocation-map digest:

```text
Expected: 52ea3797f09017db5e67f24106d2e9a44b3b9e4a4b7fbda33af94469155b85ca
Actual:   802d3d08b234524589a9e6f22786104f75c31b12b152e749ef49c056fa00cfa6
AssertionError: actual raw SHA-256 != recorded SHA-256
```

This is a genuine existing evidence/manifest inconsistency, not a learner regression or a missing
dependency. It is the same mismatch recorded before recovery. The full traceback is retained in
[pytest_full.log](recovery/logs/pytest_full.log). Recommended resolution: obtain the designated original
ZIP or another explicitly authenticated original source, confirm byte provenance and restore only
confirmed historical mismatches. Without that source, leave the gate failing and restoration pending.
The test and manifest remain unchanged.

There are **no collection errors and no skips**. The earlier missing-package errors, runtime probe-import
failures and legacy Flower collection error are resolved by the researcher's restored modules and the
corrected installation. The 13 warnings are upstream Matplotlib/Pyparsing deprecations. The prior
`206 passed, 6 skipped` remains a historical reference, not a forced target.

## 6. Wireless test results

```bash
python -m pytest -q tests/wireless
```

Exit **0**; **77 passed, 0 failed, 0 skipped, 0 collection errors**. Measured command wall time **25.988 seconds**.

All wireless numerical, protocol, allocation, persistent-state Flower adapter, local integration,
runner, paired/same-posterior probe, resume-rejection and reporting tests pass. No failures, skips or
collection errors remain in `tests/wireless`. Complete output is in
[pytest_wireless.log](recovery/logs/pytest_wireless.log).

The exact requested commands were used, without filtering or ignoring tests. Both inherited
`PYTHONDONTWRITEBYTECODE=1` and `PYTEST_ADDOPTS='-p no:cacheprovider'` to avoid cache writes; this disables
only pytest's cache provider. No algorithm/test implementation was changed. Existing tiny synthetic
computations are test execution, not new full-dataset experiment trajectories.

## 7. First-submission baseline verification

`python docs/tools/export_handoff.py --check` exits **0**: all **24 primary endpoints** and exact
communication-budget byte totals pass. The 24 selected saved configurations also validate with the
current config loader.

| Recorded profile | Dense FOLA | Byte-matched FedAvg | Array-byte budget |
| --- | --- | --- | ---: |
| MNIST selected s10/B10, seed0 | R150, 89.44% | R300, 88.23% | 2,021,090,400 |
| CIFAR-10 alpha0.01/f1, seed0 | R150, 53.10% | R300, 47.28% | 22,139,157,600 |

KL/random fixed-retention endpoints at 0.75, 0.50, 0.25, 0.10 and 0.05 also pass the checker. Submitted
MNIST s5/B5 and selected repository s10/B10 remain separate conditions. These are **recorded** results;
accuracy was not reproduced through training or model reevaluation. Endpoint verification does not
establish legacy checkpoint resumability.

Evidence: [checker log](recovery/logs/legacy_endpoints.log), [24 exact endpoint identities and hashes](recovery/legacy_endpoints.json),
[saved configuration checks](recovery/saved_profile_checks.json).

## 8. Seven joint-KL wireless runs

For each exact run, the existing read-only exporter was invoked in default **strict** mode and separately
with explicit `--records-only`. No `--write-report` export mode, training or resume was invoked.

| Scenario | Rounds | Recorded accuracy % | Modeled seconds | Records check | Strict/resume integrity |
| --- | ---: | ---: | ---: | --- | --- |
| Reference | 150 | 52.63 | 27,000 | Records-only: passes | Unverified: fails |
| U170 | 150 | 50.25 | 25,500 | Records-only: passes | Unverified: fails |
| U160 | 150 | 52.47 | 24,000 | Records-only: passes | Unverified: fails |
| U150 | 150 | 43.43 | 22,500 | Records-only: passes | Unverified: fails |
| B0550 | 150 | 47.29 | 27,000 | Records-only: passes | Unverified: fails |
| B0750 | 150 | 52.53 | 27,000 | Records-only: passes | Unverified: fails |
| B0950 | 150 | 54.01 | 27,000 | Records-only: passes | Unverified: fails |

In this table **Verified** applies only to checks that passed; **Records-only** means recorded accounting
passes while checkpoint integrity is not established; **Unverified** describes failed or insufficient
integrity evidence. Every run's records-only validation scope is `records_only_unverified_checkpoint`,
and its checkpoint digest status is `inconsistent`.

All seven strict commands exit **1**, first reporting
`ERROR: Committed metric changed: metrics/global_metrics.csv`. All seven explicit records-only commands
exit **0**, verifying exact integer count/payload bytes, cumulative array accounting, all-client records,
fixed-slot evaluated rounds and normalized sample-weighted discarded KL.

Independent raw-byte comparison identifies the same failure pattern in each run:

- R150 checkpoint JSON hash: **matches**.
- R150 checkpoint NPZ raw-byte hash: **matches**.
- Event-ledger raw-byte hash: **matches**.
- `metrics/global_metrics.csv`, `metrics/wireless_clients.csv`, `metrics/wireless_rounds.csv`: **mismatch**, totaling **21 metric-file mismatches**.

Matching state/array/ledger hashes do not override the required committed-metric checks. **No audited
run is authorized for strict resume.** No stored digest, checkpoint, event or metric file was rewritten.
NPZ checkpoint files were hashed as raw bytes, not loaded and resaved. Exact expected/actual values are
in [wireless_record_checks.json](recovery/wireless_record_checks.json).

All seven saved learning/configuration profiles validate and match on data, model, training, federation,
FOLA, compression and seed; wireless resources differ as intended. They retain 20 clients, seed0, E10/B32,
fixed gains and the illustrative `EXAMPLE_NOT_LOCKED` scenario. Modeled round targets are 180/170/160/150
seconds in the U sweep; equal R150 does not imply equal modeled time. Time/energy are simulated resource
quantities, separate from measured test/host wall seconds. No global integer-optimality or convergence
claim is implied.

Exact audited source directories:

- **Reference**: `outputs/run_wireless_cifar_eqb_joint150_fixed_v1_cifar10_a0p01_f1_joint_seed0_20261109_230207`
- **U170**: `outputs/run_wireless_cifar_joint_u170_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_115923`
- **U160**: `outputs/run_wireless_cifar_joint_u160_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_171008`
- **U150**: `outputs/run_wireless_cifar_joint_u150_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_221432`
- **B0550**: `outputs/run_wireless_cifar_joint_b0550_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_115526`
- **B0750**: `outputs/run_wireless_cifar_joint_b0750_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_170448`
- **B0950**: `outputs/run_wireless_cifar_joint_b0950_r150_v1_cifar10_a0p01_f1_joint_seed0_20261111_221033`

Compact endpoints: [wireless_endpoints.csv](recovery/wireless_endpoints.csv).
Profile comparison: [wireless_profile_checks.json](recovery/wireless_profile_checks.json).
Individual command outputs: `recovery/logs/wireless_<reference|u170|u160|u150|b0550|b0750|b0950>_<strict|records>.log`.

## 9. Historical documentation verification

Against `docs/archive/2026-11-12-snapshot/RELOCATION_MAP.json`, all **91 files are present**:
**4 raw hashes match, 87 mismatch**. Status: **Unverified historical byte preservation; restoration pending**.
The exact mismatch list and expected/actual hashes are in [archive_integrity.json](recovery/archive_integrity.json).

The recovery brief attributes previous differences to Git line-ending normalization. Current raw
hash comparisons establish the mismatches, but without the reference ZIP this task cannot independently
confirm that every difference is solely CRLF/LF conversion or establish original replacement bytes.
No in-memory normalization was used to reinterpret a raw hash as passing, and no bytes/hashes were repaired.

## 10. Final consistency and remaining issues

The final audit confirms `.gitignore`, all restored data files, protected learner/packet/allocator
source, original experiment configurations and existing reports remain unchanged. All **75 previous
onboarding artifacts** retain their original hashes. All **26,041 output files**, totaling **410,046,190 bytes**,
retain the same deterministic raw-byte tree fingerprint as at recovery intake:

```text
22d7abc459f060e0020ec7ddcbf2866ff6b58ed7410b9a92c3e58abfc5ad26bf
```

The fingerprint hashes sorted relative paths together with each file's raw SHA-256, with the procedure
recorded in the audit helper evidence. It proves preservation during this task, not that already altered
archives satisfy their original manifests. [Final preservation checks](recovery/final_preservation_checks.json).

`git diff --check` passes for the tracked working-tree changes. The staged check
`git diff --cached --check` exits **2** for **nine evidence-format diagnostics**: the literal pytest
assertion output has one trailing-whitespace line, and the newly emitted CSV has eight CRLF rows.
Those emitted bytes are preserved; no source/config patch has a whitespace defect and no whitespace
suppression rule was added. The exact diagnostics are recorded in
[staged_diff_checks.json](recovery/staged_diff_checks.json).

The final staged diff is restricted to the approved new attributes and recovery report/evidence;
no original source, config, output or prior report is staged. Earlier onboarding files remain untracked
as they were at intake. Generated editable-build metadata and Python caches, if present, are ignored
runtime artifacts and are not included in the commit.

Remaining issues are the unavailable original ZIP, 87 archived-document mismatches, 21 wireless metric
hash mismatches, the resulting one-test archival failure, and four unrelated `flwr-baselines` dependency
conflicts. Real Ray/CUDA training readiness remains unexercised. None was hidden through algorithm,
test, stored-hash or dependency-version changes.

## 11. Readiness assessment

**Further source development:** the previous missing-source and wrong-import blockers are resolved.
The repository is usable for source development with the disclosed archival test failure; it does not
have a completely passing acceptance suite or verified historical byte preservation. The single commit
records verified preventive attributes and accurate verification evidence while restoration remains pending.

**Historical checkpoints:** none of the seven audited R150 wireless runs is verified safe to resume.
Their records may be analyzed only with the explicit records-only integrity label. Other historical
checkpoints were not granted a resume status by this task.

Recovery stops here. No training, additional algorithm work, automatic push, historical reconstruction
or unrelated package maintenance is included.
