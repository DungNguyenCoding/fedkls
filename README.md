# FedKLS — Bayesian federated learning and wireless selective communication

**Repository guide (14 November 2026).** This is the research implementation for the
first-submission FedKLS benchmark and the subsequent **opt-in digital wireless**
FedKLS simulator. Its full local training, Bayesian aggregation and baseline
experiments are preserved. This cleanup reorganizes documentation and reporting;
it does **not** implement a new learning algorithm or replay completed training.

**Start with [`docs/README.md`](docs/README.md).** It links to the scientific
algorithms, complete round sequences, wireless resource model, experiment locks,
validation and current results. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
explains the purpose of *every top-level folder* and the source modules.

**New Codex conversation:** read [`docs/CODEX_SETUP.md`](docs/CODEX_SETUP.md),
[`docs/WORKFLOW.md`](docs/WORKFLOW.md), and the dated
[`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md). Model-selection examples are
in `docs/codex-profiles/`; `.codex/config.toml` contains project safety defaults,
not automatic task-based model routing.

## Choose the correct workflow

- **Legacy first submission:** FedAvg, Bayes by Backprop (BBB), dense FOLA, and
  fixed-ratio FedKLS / random-selection comparisons. Local training is dense;
  cumulative *array bytes* determine the comparison budget. Run via
  `python -m bayesfl.main --config scripts/configs/EXACT_CONFIG.yaml`.
- **Wireless extension:** the same FOLA training and KL importance, with
  integer client retention grants and bandwidth allocation under a shared slot.
  Select `wireless.enabled: true` in a reviewed configuration. This simulates
  successful digital orthogonal transmissions, **not** AirComp or a physical radio.

Experiment checkpoints and raw per-round metrics belong in `outputs/`;
reviewable, lightweight and reproducible **analysis reports belong in
[`reports/`](reports/README.md)**. A report is *not* a resumable checkpoint.

## Minimal local checks

```bash
python -m pip install -e .
python -m pytest -q tests/wireless
python -m pytest -q
PYTHONPATH="$PWD/src" python scripts/smoke_wireless_offline.py \
  --output-dir "outputs/smoke_wireless_local_unique" --rounds 3
```

Only execute the smoke with a **new** output name. Real Flower/Ray/CUDA tests
require the intended environment; missing dependencies may cause skips.
Long training runs, resume and paper plotting have specific constraints in
[`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Status and reading order

1. [`docs/ALGORITHMS.md`](docs/ALGORITHMS.md) — FedAvg, BBB, FOLA and FedKLS.
2. [`docs/WIRELESS.md`](docs/WIRELESS.md) — wireless protocol and allocator.
3. [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) — locked learning settings and comparisons.
4. [`docs/RESULTS.md`](docs/RESULTS.md) — currently recorded results and limitations.
5. [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — data, tests, run and resume rules.
6. [`reports/README.md`](reports/README.md) — analysis export contract.
7. [`docs/ARCHIVE_INDEX.md`](docs/ARCHIVE_INDEX.md) — preserved, relocated historical docs.

The original full upload `bayesfl.zip` remains the external recovery artifact for
removed scratch directories `backups/` and `modified_source/`.
