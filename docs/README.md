# Documentation index — one current source of truth

**Read these current documents in order.** Only this small group is current;
previous root, `docs/` and `docs/wireless/` write-ups and historical manifests are preserved *unchanged*
under [`ARCHIVE_INDEX.md`](ARCHIVE_INDEX.md). Historical instructions may be
superseded or describe unfinished work; do not interpret them as new results.

| Document | Question answered |
| --- | --- |
| [WORKFLOW.md](WORKFLOW.md) | Who designs, implements, launches, verifies and reviews? What does each task receive and produce? |
| [CODEX_SETUP.md](CODEX_SETUP.md) | How does a fresh Codex window recover context, choose models and use TOML profiles? |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | What is the last independently reported status, and what is *not* approved yet? |
| [TASK_TEMPLATE.md](TASK_TEMPLATE.md) | What is the input/output/acceptance contract for an approved task? |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Why does each folder/module exist? What calls what? |
| [ALGORITHMS.md](ALGORITHMS.md) | What exactly do FedAvg, BBB, dense FOLA, fixed-ratio FedKLS and selectors compute? |
| [WIRELESS.md](WIRELESS.md) | How is the legacy learner extended? What are the stages, channel/time models, packet formats and allocation constraints? |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Which MNIST/CIFAR settings are locked? Which methods/metrics are fair to compare? |
| [RESULTS.md](RESULTS.md) | What did the previously completed runs show, with what evidence and open questions? |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | How are configurations, dataset partitions, training, tests, output integrity and resume handled? |
| [ARCHIVE_INDEX.md](ARCHIVE_INDEX.md) | Where did older files move, and how can a historical claim be traced? |
| [../reports/README.md](../reports/README.md) | What should a generated review report contain, and how to produce it? |

**Source of truth hierarchy:** exact saved run configuration + raw recorded metrics,
then source code/packet tests, then current docs, then dated historical notes.
If they disagree, note the discrepancy explicitly; never silently edit results.

## Source documents preserved separately

- [`wireless/proposal/`](wireless/proposal/) — original wireless-design LaTeX
  (`wireless_model.tex`, `joint_problem.tex`, `method1.tex`, etc.). Some implemented
  choices are explicitly different; see [WIRELESS.md](WIRELESS.md).
- [`history/`](history/) — earlier versioned documentation and engineering notes.
- [`evidence/`](evidence/) — historical audit logs and snapshots.
- [`EXPERIMENT_REGISTRY.json`](EXPERIMENT_REGISTRY.json) — machine-readable
  first-submission primary-run registry. Its path must remain stable for tools.
- [`tools/export_handoff.py`](tools/export_handoff.py) — legacy code/metrics snapshot;
  distinct from the purpose-built analysis reports in `reports/`.

This documentation reorganizing does not remove the scientific trail. Old materials
are *archived*, not presented as current operating instructions.

## Persistent task context

Dated task specifications belong in [`tasks/`](tasks/README.md). Do not
confuse a **proposed** smoke/experiment with a researcher-approved run. The
researcher manually launches long jobs, and the completed evidence belongs
under [`../reports/`](../reports/README.md).
