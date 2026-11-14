# FedKLS collaboration and execution workflow

**Status:** current working agreement, 2026-11-14. **Audience:** researcher, ChatGPT Project, and any fresh Codex IDE/CLI conversation. Read `AGENTS.md` first; technical facts live in `ALGORITHMS.md`, `WIRELESS.md`, `EXPERIMENTS.md`, and the exact saved configuration/source. This document governs *work and approvals*, not the scientific equations.

## 1. Who decides and who executes?

| Role | Owns | Does not assume |
| --- | --- | --- |
| **Researcher** | Scientific priorities, acceptance of proposed algorithms, approval of experiment budgets, manual GPU execution, Git merge/push decisions | That any assistant has launched or monitored a background job without an explicit action |
| **ChatGPT Project** | Literature/mathematics review, detailed source change specifications, experimental design, analysis of delivered `reports/` evidence, next-step recommendations | That a Codex conversation inherits previous ChatGPT context or sees uncommitted local files |
| **Codex (IDE/CLI)** | Inspecting the actual checkout, implementing the approved *specific* design, focused tests, configuration and launcher preparation, read-only extraction and validation, concise reports | Authority to change scientific meaning or start long research runs on its own |
| **Persistent SSH host** | Runs processes launched manually by the researcher; retains output files if the process was correctly detached | That Codex stays alive to supervise jobs or that a detached process survives server reboot |

ChatGPT supplies the design and evaluation criteria, **not an invitation to improvise the algorithm**. Codex may report discrepancies or propose changes, but must stop and request approval if a change would affect the scientific objective, priors/precision, data partition, learning schedule, seed, packet semantics, wireless constraints or fairness of comparisons.

## 2. The task contract (all new Codex windows)

Every nontrivial task must explicitly name **purpose, inputs, outputs and acceptance criteria**. Use `docs/TASK_TEMPLATE.md` when creating a reusable task brief. For small tasks, include those fields in the first message. Source of truth is the checked-out code + exact saved config/metrics; a research specification is the approved *change target*. Report disagreements rather than silently reconciling them.

| Task kind | Inputs | Authorized outcome | Required evidence |
| --- | --- | --- | --- |
| `INSPECT` | Paths, question, Git revision | Findings; **no modifications** | Relevant source files and uncertainty |
| `IMPLEMENT` | Approved algorithm/code change specification + invariants | Scoped source/doc/test diff | Changed files, test results, unresolved risks |
| `VERIFY` | Exact revision and test commands | Tests and factual diagnosis | Exit codes, failures, skips, environment |
| `PREPARE_RUN` | Approved configuration matrix, budget, GPU policy | Config, launcher, monitor, extractor; **do not launch** | Three exact researcher-executable commands, identity/collision checks |
| `STATUS` | Exact run ID and output directory | Read-only status inspection | PID/session, exit receipt, last committed round, caveats |
| `EXTRACT` | Exact completed run ID(s) | Strict verification and a concise research report | `RESEARCH_REPORT.md` + JSON + source file hashes/metrics |

**Approval boundary:** A task asking to *prepare* a run does not authorize *launching* it. A task asking to *inspect* a running job does not authorize killing, restarting, resuming, writing to its directory, or changing config. A successful smoke does not authorize a full experiment. A completed script is not proof of successful training.

## 3. Repository information flow

```text
Researcher + ChatGPT: scientific question, proposed modification, acceptance tests
    -> docs/tasks/<task-id>.md (optional persistent approved specification)
    -> Codex: read repo, implement or prepare ONLY approved scope
    -> tests / diagnostic evidence / exact commit and config identity
    -> if training is needed: researcher manually executes LAUNCH on SSH host
    -> outputs/<unique-run>/  (raw logs, metrics, checkpoint, event ledger)
    -> researcher executes EXTRACT only after run completion
    -> reports/<unique-report>/  (compact self-contained review evidence)
    -> ChatGPT + researcher: assess, approve next experiment
```

- `src/bayesfl/`: learning and wireless implementation. No modification during documentation/reporting tasks.
- `scripts/configs/`: versioned experiment profiles. Existing study locks are immutable; new studies get new IDs.
- `scripts/`: actual entry points, launch/status/extraction utilities. Prefer reusing existing commands over a second framework.
- `outputs/`: full run data, checkpoint state, runtime logs and model-array evidence. **Never** copy raw weights into `reports/`.
- `reports/`: reviewer-facing summaries, diagnostics, configuration/hash references, and small attachable evidence ZIPs. `reports/validation/` is suitable for engineering smoke/gates; generated `reports/report_*/` contains wireless research reports. See `reports/README.md`.
- `docs/`: current specifications and operating rules; `docs/archive/` is historical provenance, **not** an active runbook.

## 4. Manual long-running experiment workflow (mandatory default)

**Preparation — Codex's job, no launch.** Given an approved exact matrix, first verify configuration schema, source commit, partition/seed identities, device selection, resource budget and output-name collision checks. Produce *three exact commands* labeled `LAUNCH`, `MONITOR`, `EXTRACT RESULTS` as well as their scripts if necessary. Commands must be tailored to the actual repository CLI, not placeholder flags. A new unique output directory is mandatory. Keep a copy of the resolved configuration, source revision and full command in run metadata.

**Launch — researcher's terminal.** Researcher runs the provided command on the persistent SSH host, typically under `nohup` (or `tmux` when interactive inspection is useful). A launch wrapper must provide durable log path, run ID, PID record and a reliable **exit status** file written when the command terminates. Capture timestamps, stderr and stdout; do not rely on `nohup.out` or absence of the PID alone as success. Be mindful of PID reuse and remote reboot. The modelled wireless seconds are not observed host/GPU seconds.

**Monitor — researcher's terminal.** Show process state, last log lines, latest *committed* round, GPU use and any explicit exit receipt. Never poll inside a Codex conversation for the full multi-hour job. Status checks must not modify the run. A missing PID with no exit receipt is **unknown**, not automatically completed.

**Extract — after termination.** Verify exit receipt, expected completed rounds, saved configuration fingerprint, metric/client/packet accounting and strict checkpoint/event/metric hashes. Invoke the existing wireless exporter, for example:

```bash
python scripts/export_research_report.py \
  --run-dir outputs/EXACT_COMPLETED_WIRELESS_RUN \
  --write-report --report-name unique_study_name
```

`EXACT_COMPLETED_WIRELESS_RUN` is a placeholder, not a runnable literal. The exporter must not rewrite source outputs. If strict validation fails or exit status is missing, report **incomplete / failed / unverified** rather than issuing a clean-success conclusion. `--records-only` is only for explicitly labeled analysis of historical altered copies, never as a resume certificate.

**Review — ChatGPT + researcher.** Upload/paste `reports/report_.../RESEARCH_REPORT.md` and, where needed, JSON and plots. ChatGPT analyzes accuracy/NLL vs rounds and *modeled* time, retained counts, sample-weighted discarded KL, packet/control bytes, allocator statuses, fairness of baseline comparisons and possible confounds; propose the next precisely controlled study. A single-seed result is not a convergence proof.

## 5. Stage gates and status labels

`PROPOSED -> APPROVED -> IMPLEMENTED/READY_TO_LAUNCH -> LAUNCHED -> RUNNING -> EXITED -> VERIFIED/FAILED/UNVERIFIED -> REVIEWED`

- **PROPOSED** is not permission to alter experiment settings or launch training.
- **READY_TO_LAUNCH** means scripts/configs were checked, not that CUDA workers ran.
- **EXITED** requires an actual process exit status or verifiable completion receipt.
- **VERIFIED** for wireless runs requires the existing strict state, metrics and ledger validators; only then discuss valid continuation under compatible caps.
- A GPU kernel probe or two-round smoke checks execution integration, not full-scale accuracy/convergence.
- Preserve completed R150 studies, the 24 historical endpoint records, partition identities and archived SHA-256 authorities.

## 6. End-of-task handoff and new-window continuity

The final Codex reply should provide: **task ID/type; Git commit and changed files; actual commands executed; pass/fail/skip counts; raw output path(s); report path(s); outstanding issues; whether training was launched (yes/no)**. For prepared runs, always include the three terminal commands and note that the researcher must execute them.

Before opening a new window: commit approved code/docs (not raw runs by default), update `docs/PROJECT_STATUS.md` only with *verified* evidence and the next gated action, preserve the relevant `docs/tasks/...` specification, and keep completed reports in `reports/`. In a fresh conversation, use `docs/CODEX_SETUP.md` as the startup entry point. Do not copy whole past chat transcripts into `AGENTS.md`.

## 7. Non-negotiable scientific boundaries

Read `AGENTS.md`. In brief: full local FOLA; `KL(global-before || local-after)` for primary FedKLS; integer count grants; omitted coordinates reconstructed from **this round's broadcast posterior**; float32 mean/**raw precision** on the wireless wire; no KL-floor substitution in transmitted precision; sample-weighted FOLA Gaussian product; exact bitmap/dense packet cost; nontrivial Ray/GPU/training changes require explicit authorization. Never silently switch to AirComp, Federated Dropout, a different precision estimator, or a different simulated channel model.
