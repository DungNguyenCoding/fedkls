# Experiment report review template

This checklist supplements the generated `RESEARCH_REPORT.md`/JSON. Fill missing
study-level interpretation **without fabricating fields**; mark evidence absent
if it is not in the raw saved configuration/metrics.

## A. What was tested?

- Research question and comparison hypothesis (not the conclusion).
- Exact complete run IDs and raw output path; report generation timestamp.
- Source revision/manifest identity, raw CSV and config hashes; any skipped checks.
- Dataset, actual partition identity, sample-count distribution, seed, model,
  number of clients, training schedule, local epochs, optimizer/clipping and FOLA mode.
- Selection mode, wireless policy, fixed channel/trace/seed, uplink/downlink
  bandwidth, PSD/noise/gains, full slot and shared upload window, control model.
- Did any run use a different round target or total modeled time? If yes,
  do not present equal-R results as an equal-time trial.

## B. Measured/recorded result

- Completed rounds; last-recorded global test accuracy (%) and mean-only NLL.
- Accuracy and NLL curves vs round and vs **observed** modeled time.
- Mean and per-client retention/count, actual score-tail objective `Σ π_k D_k(m_k)`;
  separate chosen top-m KL tail vs actual random-mask score if relevant.
- Per-round model-array bytes, control bytes and cumulative modeled seconds,
  data-plane energy (exclusions documented).
- Solver statuses, price queries, feasibility/diagnostic numerical gap;
  never write “globally optimal” without a separate proof.
- Largest negative accuracy changes, late-round variation, and which runs had
  incomplete records, report-only integrity or other warnings.

## C. Research interpretation (reviewer-authored)

1. **Supported observations** — use exact numbers from the evidence.
2. **Alternative explanations** — distinguish possible mechanisms from findings.
3. **Fairness/statistical limits** — seeds, channel realizations, equal clocks,
   coupled objectives and physical calibration.
4. **Recommended next experiment** — precise one-factor change, locked controls,
   intended metric and explicit new run name, not silently altered old results.
5. **No-go risks** — any reason data should not be used or trusted for a claim.

A report is **not** the run itself. For resumption, return to the verified
original `outputs/<run>/wireless_resume/` state and its byte-level integrity
contract, not this folder.
