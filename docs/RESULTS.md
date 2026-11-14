# Recorded evidence, current status, and research questions

**Evidence cutoff:** supplied FedKLS archives through the documented
2026-11-12 sensitivity study. This page is a consolidation of saved
experiment descriptions and the prior inspection of the upload; no new
neural-network training was performed as part of this repository cleanup.

## Recorded first-submission findings

The conference paper studied dense posterior FL, FedAvg and fixed-ratio
FedKLS/random sparse selection with 20 fully participating clients. It
reports that selecting by KL can preserve better accuracy than equal-size
random selection at higher sparsity, and that on its CIFAR-10 study r=0.25
reached a higher reported endpoint than the full-posterior comparison under
its cumulative array-byte budget. The paper's MNIST local-data condition
uses 5 examples/client; the selected repository primary MNIST figure uses
10 examples/client. These two must not be merged into one “same setting.”

The project code also provides Bayes by Backprop as a separate Bayesian
baseline and FOLA `online_recurrence` as a separate implementation variant.
Neither is the active wireless joint learner.

## Recorded R150 wireless CIFAR-10 results

| Resource scenario | Accuracy % | Final NLL | Mean retention % | Arrays GB | Control MB | Price-tolerance rounds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reference | 52.63 | 1.4045 | 47.55 | 11.438601 | 111.771 | 0 |
| U170 | 50.25 | 1.5105 | 39.14 | 9.707082 | 114.195 | 2 |
| U160 | 52.47 | 1.5052 | 31.03 | 7.997870 | 115.404 | 3 |
| U150 | 43.43 | 2.1130 | 23.02 | 6.254902 | 117.648 | 21 |
| B0550 | 47.29 | 1.9207 | 25.70 | 6.861030 | 119.192 | 27 |
| B0750 | 52.53 | 1.4623 | 35.30 | 8.901418 | 113.771 | 4 |
| B0950 | 54.01 | 1.3948 | 45.12 | 10.942543 | 112.725 | 2 |

GB/MB are decimal. Control is modeled canonical JSON payload, not actual
wireless control-plane traffic. The seven run-level audits in the historical
study report `PASS_ENGINEERING_RECORD_INTEGRITY`; all completed **150** rounds.
A separate inspection of the *uploaded* archive detected raw-checksum changes
in some checkpoint-state JSON/event ledgers caused by line-ending conversion.
These are **different evidence scopes**: saved CSV endpoints can be read and
compared, but a byte-altered archive is not automatically a valid resume
source. Do not rewrite raw hashes or mark this copy fully resumable.

### Observations, not explanations

- Reference vs U150: -9.20 percentage points at R150; reference vs B0550:
  -5.34 pp. The two harshest cases also recorded large negative adjacent-round
  changes (U150 -10.86 pp; B0550 -7.09 pp) and late-stage NLL oscillations.
- Accuracy is **not monotone** in uplink resources across these independently
  trained trajectories: U160 exceeds U170, and B0950 exceeds the 1-MHz
  reference endpoint. Optimizing weighted discarded KL does not optimize
  terminal accuracy directly.
- U150 and B0550 have 21 and 27 `price_tolerance` solver terminations,
  respectively. The recorded feasible allocation was accepted; this status is
  a numerical stopping caution, not proof of an infeasible or globally
  suboptimal integer decision.
- All seven use one seed and fixed channel gains under `EXAMPLE_NOT_LOCKED`.
  Equal 150 learning rounds do not mean equal modeled time (round targets
  differ in the U sweep). No calibrated radio deployment or statistical
  significance can be claimed.

Original evidence (preserved, including figure/CSV diagnostics):
`docs/archive/2026-11-12-snapshot/docs/wireless/JOINT_CIFAR10_SENSITIVITY_R150_20261112.md`
and `docs/archive/2026-11-12-snapshot/docs/wireless/r150_joint_20261110/`.

## Implementation status and open scientific work

The source includes opt-in wireless v2, scalar client oracles, integer packets,
joint/equal/uniform/dense policies, fixed-PSD channel model, persistent
prepared state, strict completed-round resume, Flower/local backends, and
unit/synthetic integration tests. It is **not** a new AirComp/VI/dropout
implementation. The source archive provides no warrant to call unexecuted
Flower/CUDA tests successful on a particular machine.

The next scientific decision should use **new compact reports in `reports/`**
to inspect retained counts, weighted per-client KL tails, outlier rounds,
precision and layer coverage, and fixed-time fairness. Follow-up training
comparisons require new identifiers, locked protocols and independent seeds.
For detailed experiment setup see [EXPERIMENTS.md](EXPERIMENTS.md).
