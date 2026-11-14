# Experiment design, fixed profiles, and fair comparisons

**Scope:** preserve the first-submission benchmark's selected completed results
and the later joint-wireless CIFAR-10 sensitivity runs. This page is a
*configuration contract*, not a new experiment proposal. Whenever possible,
use the exact saved `resolved_config.yaml` and partition metadata rather than
reconstructing hyperparameters from prose.

## 1. Two deliberately different evaluation axes

| Study | Independent resource | Observable outcome | Do **not** assume |
| --- | --- | --- | --- |
| First submission | Cumulative *float32 model-array bytes*, including multicast + client uplinks | Global test accuracy at last affordable round, accuracy-vs-GB | Equal byte budget means equal wireless time |
| Wireless joint | Fixed physical scenario, per-round slot `T`, bandwidth `B_max`, channel/gain/compute/control model | Accuracy/NLL vs rounds, modeled time, retained fractions, discarded KL, arrays/control bytes | Equal rounds mean equal modeled seconds; lower discarded KL necessarily improves accuracy |

## 2. Selected first-submission learning profiles

| Setting | MNIST selected repository primary | CIFAR-10 selected repository primary |
| --- | --- | --- |
| Model | `mnist_cnn_16_32_128`; `d=80,202` | `paper_basiccnn`; `d=878,538` |
| Clients/participation | 20/20 | 20/20 |
| Partition | `fixed_labels`, 1 label/client, **10 examples/client**, seed 0 | `paper_dirichlet`, alpha **0.01**, local fraction **1.0**, seed 0 |
| Local training | E=5, B=10, SGD | E=10, B=32, SGD |
| FOLA learning rate | 0.10 constant | 0.02 cosine, floor 1e-4, horizon 400 |
| FedAvg learning rate | 0.10 constant | 0.01 constant |
| FOLA global-prior coefficient | 0.01 | 0.01 |
| FOLA mode | `paper_reference` | `paper_reference` |
| Gradient clipping: FOLA / KL / random | Disabled for selected MNIST work | Norm 10 |
| Gradient clipping: selected FedAvg | Norm 10 (recovered selected curve) | Norm 10 |
| Keep ratios for KL/random sparse FOLA | 0.75, 0.50, 0.25, 0.10, 0.05 | Same |
| Reference | Dense FOLA R150 / byte-matched FedAvg R300 | Same |
| Modeled total array-byte budget | **2,021,090,400 B** | **22,139,157,600 B** |

The **submitted paper's MNIST condition** describes *five examples per client*
and batch size 5. That is **not** the same condition as the selected repository
MNIST s10/seed0/B10 experiments above. The historical s5/seed3, N100, older
MLP/ResNet and R120 investigations remain archived, not silently relabeled.

The source's CIFAR label partition can floor class allocations and backfill
empty clients: do not assert disjoint/equal 2,500 client samples without
verifying the actual saved partition. `local_data_fraction=1.0` describes no
additional subsampling after allocation; it is **not** a participation fraction.
The project guardrail is E<=10 unless an explicit separate experiment changes
it. Primary registry: [`EXPERIMENT_REGISTRY.json`](EXPERIMENT_REGISTRY.json).

### Legacy controls and byte counting

The comparison consists of dense FOLA, dense FedAvg, fixed-ratio KL selection,
and equal-cardinality random sparse FOLA. Same seeds/partitions/learning
parameters (except method-specific model and LR settings) are essential for a
meaningful within-study comparison. The legacy communication model assumes
one multicast full model per round, plus separate client uplinks. It has no
wireless channel fading or modeled transmission deadline.

A shorter message permits more *rounds* within the byte limit. This alone does
not establish a better anytime test accuracy or guarantee convergence; plot the
full curve rather than only the endpoint.

## 3. Wireless research profile and already completed sensitivity study

The primary current research algorithm is `fola` + `wireless.policy: joint` +
`compression.selection_rule: kl_global_local`. In the completed seven CIFAR
runs, learning matches the CIFAR primary profile above (20 clients, alpha=0.01,
seed0, E10/B32, FOLA), with **fixed** user-supplied channel gains and an
illustrative physical scenario labeled `EXAMPLE_NOT_LOCKED`.

| Study | Uplink Bmax | Shared upload window U | Recorded R150 accuracy |
| --- | ---: | ---: | ---: |
| Reference | 1.00 MHz | 58.973 s | **52.63%** |
| U170 | 1.00 MHz | 48.973 s | 50.25% |
| U160 | 1.00 MHz | 38.973 s | 52.47% |
| U150 | 1.00 MHz | 28.973 s | **43.43%** |
| B0550 | 0.55 MHz | 58.973 s | **47.29%** |
| B0750 | 0.75 MHz | 58.973 s | 52.53% |
| B0950 | 0.95 MHz | 58.973 s | **54.01%** |

The uplink-window sweep holds Bmax fixed; the bandwidth sweep holds U fixed
(and retains a 1 MHz downlink). It is **not** a simultaneous two-dimensional
randomized trial. The 1-MHz reference has a 180-s total round target; lower-U
cases use 170/160/150-s rounds. A 150-round result therefore spans different
modeled total times across some cases. These are single seed/one fixed channel
realizations; no statistical significance or real-radio result is established.
Detailed archived observation: `docs/archive/2026-11-12-snapshot/docs/wireless/JOINT_CIFAR10_SENSITIVITY_R150_20261112.md`.

## 4. Meaningful comparison and required measurements

A valid report identifies: exact run names, hashed resolved configurations,
Git/source identity if known, dataset/partition/seed, learner, selector and
allocator policy, model `d` and samples/clients, `round_target_s`, actual
shared U, Bmax, downlink/control model and channel mode, total completed
rounds, mean-only global accuracy and NLL, retention and client KL tails,
model-array bytes, logical control bytes, modeled seconds and data-plane
transmit energy. Report allocator statuses and price-query counts separately.

For fairness, use **matched learning and scenario parameters** and compare
common observed round/time checkpoints without interpolation beyond data.
Do not select best test accuracy as the only endpoint; provide terminal,
best-recorded (descriptive), and trajectory fluctuation diagnostics.

## 5. Future proposals versus established results

The saved study raises a research question: why do severe constraints,
particularly U150/B0550, show large late-round accuracy drops? Candidate
hypotheses include repeated omitted-coordinate effects, client-layer
coverage, KL tail concentrations, and interactions with Bayesian precision;
these are **not identified causes**. Follow-up designs might use matched
frozen-round reconstructions, layer/client diagnostics, independent seeds,
channel variation and new baselines, all as **new study IDs**. Avoid adjusting
old training traces or changing the allocator inside a recorded reference run.

See [RESULTS.md](RESULTS.md) for what the previous reports actually verified.
