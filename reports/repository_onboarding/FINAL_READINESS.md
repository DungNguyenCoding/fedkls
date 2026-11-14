# FedKLS — Final Readiness

**Repository verification and actual host CUDA computation pass.** The last historical document was
restored from an existing authenticated local installer archive. Document integrity is **91/91**;
the full suite has **217 passed**, wireless **77 passed**, all **24 benchmark checks pass**, and all
**seven wireless runs pass strict checkpoint and resume-loader validation**.

Generated **2026-11-14T17:23:41+09:00**, Asia/Seoul. Base commit: `02ce3de8a90d37fa311f7ff3287df3efd241595c`;
branch: `fix/historical-evidence-newlines`. The initial tracked tree/index were clean; 75 pre-existing
untracked onboarding artifacts were preserved. This task changes only the verified archived document
and new report artifacts. No training, actual continuation, dependency installation or automatic push occurred.

## Readiness assessment

| Activity | Assessment | Evidence boundary |
| --- | --- | --- |
| Source development | **Ready** | Full and wireless suites pass; historical document integrity is complete. |
| New training | **Conditionally ready** | Both GPUs execute real PyTorch CUDA math/backward correctly. A full Flower/Ray/CUDA training workflow was not run; a new run still requires an approved config, identity and resource plan. |
| Historical resume | **All seven audited R150 runs eligible** | Existing complete strict checks pass under their saved scientific conditions and compatible allowed cap extensions. No actual continuation was performed. |
| Overall environment | **FedKLS requirements satisfied; unrelated conflicts remain** | `flwr-baselines` has four existing dependency conflicts. They were not repaired or hidden. |

## Final historical document investigation and restoration

Target:

```text
docs/archive/2026-11-12-snapshot/docs/DOCUMENTATION_VALIDATION.md
```

Expected and restored raw SHA-256:

```text
3ecf9ba6c65c5c3700a03134165a05c0f09fd2b52d5b7f3d66bce35524a70048
```

The investigation checked current Git refs, all local branches and reflog-reachable objects; local
duplicate/history/backup paths under `/home/micl/DungNDH` and user attachments; and named document
members in three already available documentation/wireless archives. **14 candidate records** were
examined. Neither of the two Git-history document blobs matched. **Three existing copies matched
the expected raw digest exactly**:

1. `/home/micl/DungNDH/micl/bayesfl/docs/DOCUMENTATION_VALIDATION.md`.
2. `/home/micl/DungNDH/micl/fedkls_wireless_update_v1/payload/docs/DOCUMENTATION_VALIDATION.md`.
3. The corresponding installer ZIP member used for restoration:

```text
Archive: /home/micl/DungNDH/micl/FedKLS_Wireless_Update_v1.zip
Member:  fedkls_wireless_update_v1/payload/docs/DOCUMENTATION_VALIDATION.md
Archive SHA-256:
ce4a89f177c1da30e7766808ff70f9ceda5f0a1b4131598d733b6a815378f9df
```

The exact member bytes were copied unchanged after backing up the current file. No approximate text,
newline reconstruction, encoding change, hash rewrite or test modification was used. The relocation
manifest remains byte-identical. Full candidate identities, raw hashes and search scope are retained in
[document_investigation.json](final_readiness/document_investigation.json).

### Why uniform newline recovery could not work

| Version | Bytes | CRLF endings | Lone LF endings |
| --- | ---: | ---: | ---: |
| Before restoration | 2,867 | 0 | 38 |
| Authenticated original | 2,896 | 29 | 9 |

The authentic document has **mixed line endings**. Its text becomes byte-identical to the previous copy
when CRLF pairs are compared as LF; this comparison was diagnostic only. Restored bytes came directly
from the matching ZIP member. Neither an all-LF nor an all-CRLF candidate could reproduce that original
mixed pattern. The likely cause is newline normalization during a prior import/transfer/Git workflow;
the available evidence does not identify the exact tool or step that performed it.

The previous copy's raw hash was
`c93b9ac8555a62d10bd3b37e69c799a7b440c78ddb94761bfe860f0f8470fd99`.
Its verified backup is:

```text
/tmp/fedkls_final_document_backup_3bnwiw_x/DOCUMENTATION_VALIDATION.before.md
```

An independent pass against the unchanged relocation map now confirms **91/91 raw hashes matching**,
and the unmodified archival test passes. There is no remaining document-provenance mismatch in that
manifest. [Archive verification](final_readiness/archive_verification.json).

## Actual GPU kernel execution: host versus sandbox

Both probe scopes verified the interpreter and module origin before attempting CUDA:

- Python: `/home/micl/anaconda3/envs/dungndh/bin/python`, version **3.10.20**.
- Conda: **`dungndh`**.
- FedKLS origin: `/home/micl/DungNDH/fedkls/src/bayesfl/__init__.py`.
- PyTorch: **2.11.0+cu128**, compiled CUDA **12.8**; compiled architectures include **`sm_120`**.
- Host driver: **580.65.06**; two NVIDIA GeForce RTX 5090 GPUs, compute capability **12.0**.

The **sandbox** probe sees no CUDA devices and exits **2** with scope
`cuda_unavailable_in_execution_scope`; its NVML warning and `nvidia-smi` exit 9 are recorded separately.
No sandbox kernel success is claimed. The approved **host** probe uses the same environment, sees both
GPUs, executes the operations below and exits **0**.

For each GPU, a separate CUDA device context performed:

1. Device-local allocation and construction of two 64×64 float64 tensors with deterministic values.
2. CUDA matrix multiplication `output = a @ b`.
3. Scalar `loss = output.square().mean()` and `loss.backward()` on both input tensors.
4. Checks that tensors, results and gradients are on the intended GPU and all values are finite.
5. CPU reference matrix multiplication and backward on the same input values; output and both gradients compared with `rtol=atol=1e-10`.
6. Successful `torch.cuda.synchronize(device)` before/after computation and cleanup, without CUDA errors.

| GPU | Allocation / matmul / backward | Finite values | CPU output/gradient match | Synchronization | Measured wall s |
| --- | --- | --- | --- | --- | ---: |
| 0 — NVIDIA GeForce RTX 5090 | Pass | Pass | Pass (max error 0) | Pass | 1.227 |
| 1 — NVIDIA GeForce RTX 5090 | Pass | Pass | Pass (max error 0) | Pass | 0.234 |

Both devices produced loss **305.5504357897589**, output sum **-13.328125**, finite gradients and **zero
observed maximum absolute error** against the CPU output and both CPU gradients. Measured per-device
durations include initialization/reference work; they are not performance benchmarks or simulated
wireless time. Tensor math used no model, optimizer, dataset, checkpoint or training loop.

Evidence: [host_cuda.json](final_readiness/host_cuda.json), [sandbox_cuda.json](final_readiness/sandbox_cuda.json),
[host execution transcript](final_readiness/logs/host_cuda.transcript.json),
[sandbox transcript](final_readiness/logs/sandbox_cuda.transcript.json),
[exact probe source snapshot](final_readiness/logs/cuda_probe_source.txt).

## Final repository and benchmark verification

| Command | Exit | Result | Measured wall s | Exact transcript |
| --- | ---: | --- | ---: | --- |
| `python -m pytest -q` | 0 | **217 passed** | 24.407 | [pytest_full](final_readiness/logs/pytest_full.transcript.json) |
| `python -m pytest -q tests/wireless` | 0 | **77 passed** | 51.327 | [pytest_wireless](final_readiness/logs/pytest_wireless.transcript.json) |
| `python -m pytest -q tests/test_repository_layout.py::test_relocated_historical_docs_are_byte_preserved` | 0 | **1 passed; 91/91 hashes independently verified** | 0.377 | [archive_test](final_readiness/logs/archive_test.transcript.json) |
| `python docs/tools/export_handoff.py --check` | 0 | **24 endpoints and byte budgets pass** | 0.220 | [legacy_endpoints](final_readiness/logs/legacy_endpoints.transcript.json) |

Both requested suites have **zero failures, skips or collection errors**. The former archival failure is
resolved by the authenticated file restoration; its expected hash and assertion are unchanged.
The full suite reports 13 upstream Matplotlib/Pyparsing deprecation warnings. Tests use
`PYTHONDONTWRITEBYTECODE=1` and `PYTEST_ADDOPTS='-p no:cacheprovider'` to avoid bytecode/cache writes;
no tests were filtered or weakened. Console output is saved exactly in each transcript JSON's
`stdout_utf8` field, including whitespace.

The existing checker again verifies **24 legacy benchmark endpoints and their exact array-byte budgets**.
These remain recorded results, without rerun accuracy or training. MNIST s5/B5 and selected s10/B10
conditions and the legacy/wireless comparison axes remain distinct.

## Seven-run strict historical integrity and resume status

Each run again passed the existing default strict CLI:

```text
python scripts/export_research_report.py --run-dir <exact-saved-run>
```

All seven exits are **0**; no records-only fallback was used. Recorded metrics/accounting, checkpoint
JSON, raw array bytes, event ledgers and tracked metric hashes remain valid. Strict analysis reports
`verified_byte_digests` with no issues.

| Run | Recorded metrics | State / array / ledger digests | Strict resume loader |
| --- | --- | --- | --- |
| Reference | Pass | Pass | Eligible |
| U170 | Pass | Pass | Eligible |
| U160 | Pass | Pass | Eligible |
| U150 | Pass | Pass | Eligible |
| B0550 | Pass | Pass | Eligible |
| B0750 | Pass | Pass | Eligible |
| B0950 | Pass | Pass | Eligible |

The existing `WirelessState(..., resume=True)` loader was also invoked read-only with saved configs,
actual canonical partition-content hashes, channel/trace identities and the expected model layout.
Every run passed protocol, configuration fingerprint, partition/trace/layout, raw digests, array
validation, restored snapshot and cap checks. Only in-memory state was loaded; no runner, local fit,
evaluation, metric append, checkpoint save or actual continuation followed.

The saved R150 caps yield `max_rounds`. Future continuation requires a separately approved compatible
round/time cap extension while preserving all scientific settings. Strict eligibility is distinct from
actual continued training or a full Flower/Ray/CUDA workload test.

Exact saved run identities, component checks and evidence hashes are in
[wireless_strict_checks.json](final_readiness/wireless_strict_checks.json). Individual strict CLI outputs
are `final_readiness/logs/wireless_<label>_strict.transcript.json`; combined read-only restore evidence is
[strict_wireless_checks.transcript.json](final_readiness/logs/strict_wireless_checks.transcript.json).

## Environment warnings and remaining scope

All **26 checked direct FedKLS/applicable Flower simulation dependency records** satisfy their installed
version constraints. No dependency was installed, upgraded, downgraded or automatically repaired.
However, `python -m pip check` still exits **1** for the separately installed `flwr-baselines 1.0.0`:

| Its requirement | Installed |
| --- | --- |
| pandas >=1.5.3,<2.0.0 | 2.2.2 |
| pillow ==10.2.0 | 12.1.1 |
| torch ==2.4.1 | 2.11.0+cu128 |
| torchvision ==0.19.1 | 0.26.0+cu128 |

That package is not a declared FedKLS dependency. Existing upstream plotting deprecations and
sandbox/user-cache permission warnings remain; they did not cause a FedKLS test or host CUDA failure.
The sandbox NVML/device restriction is not a host driver failure. Global environment consistency is
therefore not claimed despite passing FedKLS checks. [Dependency checks](final_readiness/dependency_checks.json),
[pip check transcript](final_readiness/logs/pip_check.transcript.json).

Real end-to-end Flower/Ray multi-process GPU training, prolonged workloads, performance and convergence
remain untested here. No training queue or historical continuation was started. These boundaries qualify
new-training readiness; they do not negate the measured per-GPU kernel and strict resume results.

## Preservation, Git review and completion

The preservation audit confirms:

- **1,625 protected non-target tracked files unchanged**, including all 55 active source files and 936 files under `scripts/configs/`.
- All **26,041 output files**, **410,069,318 bytes**, unchanged, including every checkpoint, ledger, metric and partition file.
- All **181 prior report artifacts** unchanged; all 75 pre-existing untracked artifacts preserved.
- The only original tracked-file modification is the exact historical document restoration; `.gitignore`, `.gitattributes`, tests and integrity authorities remain unchanged.

The full output raw-byte tree fingerprint is identical before/after:

```text
7ea3223e7422caef16bf529302f734374bfbf164e6a4a484cb057d4752974a8b
```

The method hashes sorted relative paths plus each raw file SHA-256. Details and backup verification
are in [preservation_checks.json](final_readiness/preservation_checks.json) and
[baseline.json](final_readiness/baseline.json).

The document's `text: unset` attribute preserves its original mixed endings. Its staged/committed raw
blob must match the authoritative SHA-256 exactly. Git's default whitespace check flags its **29 authentic
CRLF lines**; those bytes are retained. New report artifacts are checked separately for clean formatting.
No whitespace-suppression rule or evidence normalization is added. The reviewed commit is restricted to
the authenticated document and new final-readiness report/evidence, without pushing automatically.

The final commit is the one containing this report, with its exact SHA supplied in the completion response:

```bash
git log -1 --format=%H -- reports/repository_onboarding/FINAL_READINESS.md
```

**Final status:** source-development gates and both GPU kernel sanity tests pass; all 91 historical
documents are authenticated; all seven audited checkpoints remain strictly eligible. New training remains
conditional on an approved run and the unexercised end-to-end workflow. Actual continuation was not performed.
