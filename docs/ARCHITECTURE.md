# Repository architecture and folder responsibilities

## Top-level folders

| Path | Responsibility | Write policy / cautions |
| --- | --- | --- |
| `.codex/` | Trusted-repository Codex safety defaults (approval and workspace sandbox only) | No automatic model routing; see `docs/CODEX_SETUP.md` |
| `src/bayesfl/` | Actual Python implementation of learning, Gaussian math, packet selection, evaluation, state management | Scientific core; change only with explicit experiment intent and regression tests |
| `src/bayesfl/wireless/` | Opt-in digital wireless extension: channel, integer allocation, multi-phase clients, packets, runtime, accounting | Separate from legacy learner; no implicit AirComp, radio noise or dropout |
| `scripts/` | Entry scripts for configuring, validating, running, inspecting, plotting and exporting studies | Keep scripts versioned and deterministic; long queues only by explicit decision |
| `scripts/configs/` | YAML profiles for saved legacy and wireless studies | Preserve historical generated scenarios and explicit source identities; do not rename referenced runs |
| `scripts/queues/` | Recorded sequential-per-GPU queue definitions and launcher inputs | Never auto-run historical queues or combine unrelated runs |
| `tests/` | Numerical, protocol, dataset/profile, state/resume and integration regressions | Include small synthetic integration tests; skipped Flower/CUDA is not a pass |
| `outputs/` | **Raw experiment evidence**: model arrays/checkpoints, resolved configuration, partitions, per-round metrics, ledger, resume state | Protected; no reports-generated rewrites; retains existing run paths and history |
| `outputs/partitions/` | Cached client partitions and metadata including content checksums | Exact identities are part of reproduction; do not regenerate silently |
| `reports/` | **Analysis-facing deliverables**: small summaries, selected source CSVs, hashes, diagnostic tables, comparison reports and attachable ZIPs | Generated from completed runs; never the sole recovery backup; ignore generated content in Git by default |
| `plots/` | Rendered historical/publication plots and explicitly requested future figures | Derived artifacts, not a source of checkpoint truth |
| `logs/` | Console/queue log files from execution | Operating diagnostics, not training evidence; keep out of reports except cited excerpts |
| `validation/` | Historical validation receipts/hashes and gate results | Dated evidence; not a substitute for retesting after a change |
| `docs/` | **Current** mathematical and engineering definitions | This index is the entry point; keep active pages small and authoritative |
| `docs/tasks/`, `docs/codex-profiles/` | Approved task briefs and optional user-profile templates | Neither is an active training job or automatically installed user settings |
| `docs/archive/` | Original superseded documentation and relocation map | Read-only history, not runnable instructions |
| `docs/history/`, `docs/evidence/` | Earlier stage histories and raw audit materials retained for provenance | Do not overwrite or promote old claims to new experimental evidence |
| `docs/wireless/proposal/` | Supplied preimplementation wireless mathematical proposal (LaTeX) | Research reference; distinguish designed ideal model from implemented adapters |
| `docs/tools/` | Legacy source/metrics handoff exporter | Existing compatibility tool, not the per-study report generator |
| docs/archive/.../ root manifests | Historical installer/config/source integrity records | Preserved byte-identically for provenance, but no longer clutter the repository root |
| root `README.md`, `AGENTS.md`, build files | Entry point, scientific editing guardrails, package configuration | Only active root guide files; historical root manifests and notes live in the archive |

**Removed from cleaned repository:** `backups/`, `modified_source/` (working
copies, not imported packages). Their file identities are recorded in
[ARCHIVE_INDEX.md](ARCHIVE_INDEX.md). The original uploaded archive remains available
as recovery evidence. Non-imported `src/*.before_*` snapshots have been moved to the
dated documentation archive, outside live Python package code.

## Source-module map

| Code | Purpose |
| --- | --- |
| `main.py`, `config.py`, `logging_utils.py` | CLI → strict YAML → experiment setup/routing, output paths, environment metadata |
| `data/{datasets,partition,transforms}.py` | Obtain MNIST/CIFAR data, immutable client assignment, preprocessing, deterministic loaders |
| `models/{factory,mnist_*,paper_cnn,cifar_resnet,bayesian_layers}.py` | Model architectures and Bayesian-layer variants; `paper_basiccnn` matches selected CIFAR profile |
| `training/deterministic.py` | FedAvg local SGD on deterministic model |
| `training/bbb.py`, `posterior/scale_mixture.py` | Variational Bayes by Backprop local training and prior complexity |
| `training/fola.py` | FOLA MAP local loss plus diagonal precision from task-gradient squares |
| `posterior/packing.py`, `posterior/gaussian.py` | Flatten/unflatten parameter layouts, mean/precision layout, numerical Gaussian functions |
| `posterior/sparse.py` | Legacy fixed-ratio KL/random selection, bitmap v1 packets, global prior fill |
| `posterior/aggregation.py` | Original FOLA weighted Gaussian-product reducer |
| `client.py`, `server.py`, `strategies/research_strategy.py` | Legacy Flower fit/evaluate/aggregate and byte-budget runner |
| `evaluation.py`, `metrics.py`, `experiment_state.py` | Global evaluation, logged metrics, legacy completed-round resume |
| `wireless/config.py`, `channel.py`, `payload.py` | Validated wireless physical/compute parameters and integer bit-cost models |
| `wireless/oracle.py`, `allocation.py` | Frozen client KL curves, local price/count oracle and feasible allocator |
| `wireless/client.py`, `transport.py`, `protocol.py` | Prepared-state lifecycle, local/Flower transport and validated v2 packet/grant semantics |
| `wireless/controller.py`, `runner.py`, `state.py` | Wireless round sequencing, study execution, resource ledgers and strict resume |
| `wireless/reporting.py`, `wireless/research_report.py` | Independent read-only recorded-results inspection and evidence export |

## End-to-end routing

```text
reviewed YAML / CLI
   │
   ├── wireless absent/disabled ──► legacy Flower server/strategy
   │                                  │
   │                            clients train FedAvg / BBB / FOLA
   │                                  │
   │                         [optional fixed-ratio KL upload]
   │                                  │
   │                            server reconstruction/aggregation
   │                                  └──► evaluate → raw metrics → legacy resume
   │
   └── wireless.enabled=true ──► wireless runner / round controller
                                      │
                    broadcast → PREPARE (full local fit, frozen score state)
                                      │
                       QUERY (small count/price responses)
                                      │
                       ALLOCATE (integer m, bandwidth)
                                      │
                         GRANT → UPLOAD (encoded values)
                                      │
                  validate → reconstruct → FOLA aggregate
                                      │
                          evaluate → strict round commit
                                      └──► outputs/run_wireless_.../
                                                      │
                                read-only exporter ───┴──► reports/<unique-report>/
```

Other stages, including historical plotting, may consume `outputs/` but do not
alter the learning algorithm. [`WIRELESS.md`](WIRELESS.md) and
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) specify the detailed sequence.
