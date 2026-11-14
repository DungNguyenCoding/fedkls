# FedKLS repository research invariants

Read `docs/README.md`, `docs/ALGORITHMS.md`, `docs/WIRELESS.md`,
`docs/EXPERIMENTS.md`, and `docs/REPRODUCIBILITY.md` before editing an
experiment's semantics. Use `reports/README.md` for evidence exports.

## Hard constraints

- Do not modify an experiment's learning algorithm, client partition, seed,
  clipping, schedule, optimizer, or communication budget through a documentation
  cleanup. Preserve selected first-submission runs and every completed R150
  wireless sensitivity trajectory. Do not overwrite raw `outputs/run*/` data.
- FOLA uses a **global Gaussian prior**, trains the *full* local model, and
  aggregates diagonal **raw precision** and mean with its existing epsilon
  convention. Do not replace the squared minibatch-mean gradient estimate with
  per-example Fisher or another estimator without an explicitly separate study.
- FedKLS's primary score is `KL(global-before || local-after)` at each coordinate;
  `kl_local_global` is a distinct historical option, not a synonym. Selection
  removes **messages**, not model weights or local computation. Missing client
  coordinates are filled from the **same round's broadcast** state.
- Wireless v2 grants exact integer counts; do not convert them to/from a
  rounded keep ratio. Do not transmit full unselected local posteriors, re-train
  for price queries, move score-only floors onto uploaded raw precision, silently
  drop a client, change the channel upon infeasibility or assume global integer
  optimum from a floating-point numerical gap.
- Wireless data, logical control and modeled time/energy accounting are distinct.
  This is ideal **digital orthogonal** transmission and fixed PSD, not AirComp,
  observed PHY throughput, or guaranteed convergence.
- Strict resume requires *raw byte* checkpoint/metric/event hashes. Never
  normalize line endings, rewrite hashes, or treat a records-only report as
  resumable evidence. Use new run identities and completed-round commits.
- `training.local_epochs <= 10` remains the working compute limit; do not silently
  alter locked profiles. Original paper MNIST s5/B5 and selected repository
  MNIST s10/B10 are distinct conditions.

## What goes where

- `src/`: reusable algorithms and wireless protocol; `tests/`: regression checks.
- `scripts/` and `scripts/configs/`: commands and **explicit** run settings.
- `outputs/`: original full training outputs and checkpoint state.
- `reports/`: generated compact summaries, CSV evidence and review bundles;
  no checkpoints, NPZs, or raw model arrays. Never manufacture a clean-integrity
  status for a byte-altered archive.
- `docs/`: current scientific documentation and archived historical notes.

A non-scientific refactor must leave the protected learner/packet/allocator source
byte-identical and pass existing focused tests. If an empirical result is merely
recorded rather than rerun, report it as recorded and distinguish simulated
resources from measured wall time.

## Multi-conversation work and manual experiment policy

At the start of a fresh Codex window, read `docs/WORKFLOW.md`,
`docs/PROJECT_STATUS.md`, and `docs/CODEX_SETUP.md`; use an approved
`docs/tasks/TASK-*.md` brief or an explicit equivalent input/output contract.
The researcher and ChatGPT own the scientific design; implement only the
approved scope. `PREPARE_RUN` means create and verify **LAUNCH / MONITOR /
EXTRACT RESULTS** commands, not execute long-running training. The researcher
launches training manually on the SSH host and returns `reports/` evidence for
scientific review. Never assume a new window inherited earlier chat context.
