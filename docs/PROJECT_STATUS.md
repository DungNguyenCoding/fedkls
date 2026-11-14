# FedKLS current handoff state

**As of 2026-11-14 (Asia/Seoul); human-maintained status snapshot, not a live process monitor.** At the beginning of any new Codex window, check the actual repository commit, `git status`, report files and running jobs before treating this page as current. New evidence supersedes this snapshot; never invent an approval or training result.

## Last established verification

Source: `reports/repository_onboarding/FINAL_READINESS.md` (verified and uploaded to the research conversation, 2026-11-14). It reported:

- Python imports: the editable `bayesfl` resolves to the new FedKLS repository.
- Full suite: **217 passed**; wireless subset: **77 passed**.
- Archived-document hashes: **91/91**; recorded original benchmark endpoint/byte-budget checks: **24/24**.
- Seven joint-KL CIFAR-10 R150 runs: **7/7 strict checkpoint, metric and resume-loader integrity pass** *under their saved settings*. No continuation was executed.
- Both RTX 5090 host GPUs successfully ran PyTorch CUDA matmul and backward. **This did not test full Flower/Ray/CUDA training.**
- Four unrelated `flwr-baselines` version conflicts persist in the Conda environment; avoid package churn unless necessary.

These are **past recorded checks**. Rerun necessary tests on the current commit before modifying code or launching new experiments.

## Last known pending execution gate

Source: `reports/validation/GPU_INTEGRATION_SMOKE.md` (preflight report supplied in research conversation; verify whether present in this checkout). The existing CPU synthetic Flower/Ray smoke did not exercise CUDA. A **proposed but unexecuted** bounded GPU smoke uses MNIST, 10 fully participating one-sample clients, 2 rounds, 1 local epoch, model `mnist_cnn_16_32_128`, FOLA/primary KL/joint wireless allocation and GPU 0. Reported proposed files: `reports/validation/gpu_integration_smoke/PROPOSED_SMOKE.yaml` and `PROPOSED_LAUNCH.py`. These paths/contents must be inspected in the actual checkout before use; this handoff file does not certify them.

**Researcher preference at handoff:** additional planning/development work may happen **before** the GPU integration smoke and before any full research training. **No training launch is authorized by this document.** If a new development change is approved, test that code first and reconsider the smoke's configuration against the modified revision.

## Research emphasis after execution readiness

Explore why restrictive uplink resources (shorter upload slots and lower bandwidth) change learning trajectories in the fixed-channel CIFAR-10 joint-KL study. The saved reference R150 endpoint was **52.63%**, U150 **43.43%**, and B0550 **47.29%**; all are *single-seed recorded outcomes*, not re-executed performance or proved causes. Preserve sample weighting, integer packet accounting, FOLA estimator and comparator fairness. Source: `docs/RESULTS.md` and the strict seven-run reporting evidence.

## Next action (requires a new explicit task)

1. Read `docs/WORKFLOW.md` and any newly approved `docs/tasks/TASK-*.md`.
2. If only onboarding, inspect source/docs/status and **stop** without modifications or training.
3. For an approved change, implement exact scoped specifications + tests, then report commit/evidence.
4. For an approved experiment, prepare three researcher-run commands **LAUNCH**, **MONITOR**, **EXTRACT RESULTS**; **do not launch** long training from Codex by default.
5. The researcher manually runs and uploads the `reports/` evidence to ChatGPT for scientific review.

## Update discipline

When a task is genuinely complete, update **only factual state** here: date, source commit, verified tests, report path, exact run ID, remaining risks and next approval gate. Do not delete older reports or rewrite prior conclusions. If this file disagrees with current code, an actual run manifest or the latest verification log, report the discrepancy and use the primary evidence.
