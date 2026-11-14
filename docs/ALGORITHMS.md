# Implemented learning algorithms and communication selection

This document describes **actual source behavior**, distinguishing the scientific
papers from implementation choices. The model is centralized only in the sense of
global *evaluation*: training data stay partitioned among clients. Training and
selection operate on a fixed parameter layout of `d` scalar coordinates.

## Notation and shared assumptions

- `K` clients; client `k` holds `D_k` with `n_k` training examples, and the
  normalized contribution weight is `π_k = n_k / Σ_j n_j`.
- Round `t` begins with broadcast mean `μ_G,t` and **raw diagonal precision**
  `ω_G,t` for FOLA; where a Gaussian interpretation is valid, variance is
  `v = 1/ω` (only strictly positive precision defines a proper Gaussian).
- A local posterior approximation is `(μ_k,t, ω_k,t)`; the *full local model*
  is optimized before any compression mask is selected.
- `m_k` is the integer number of coordinates sent by client `k`. Fixed-ratio
  legacy uses `m = ceil(r*d)`; wireless v2 uses an explicit grant `m_k`.

### Core references from the project

- McMahan et al., *Communication-Efficient Learning of Deep Networks from
  Decentralized Data* — FedAvg.
- Blundell et al., *Weight Uncertainty in Neural Networks* — BBB variational
  posterior and scale-mixture prior.
- Liu et al., *A Bayesian Federated Learning Framework with Online Laplace
  Approximation* — FOLA prior iteration and Gaussian-product aggregation.
- First-submission *KL-Guided Selective Posterior Transmission for Bayesian
  Federated Learning* — fixed-ratio FedKLS and KL(global||local) omission cost.
- The wireless proposal is under `docs/wireless/proposal/`; **adaptations to it**
  are recorded in [WIRELESS.md](WIRELESS.md).

## A. Deterministic FedAvg (implemented)

1. Server broadcasts deterministic weights `θ_G,t`.
2. Each client initializes its model from that same broadcast, trains for
   configured local epochs/batches using SGD, and returns its full parameter
   arrays. Scheduler, clipping and learning rate are explicit YAML settings.
3. Server forms a sample-size-weighted average:

   `θ_G,t+1 = Σ_k π_k θ_k,t`.

4. Server centrally evaluates and records round metrics. The first-submission
   FedAvg endpoint is chosen by **equal modeled array bytes**, not equal rounds
   or wireless seconds. When wireless is enabled, FedAvg is supported only
   in the **dense** policy.

**Code:** `training/deterministic.py`, `client.py`,
`strategies/common.py`, `server.py`.

## B. Bayes by Backprop (BBB, implemented historical baseline)

For each Bayesian weight, the mean-field approximation is
`q(w) = N(μ, diag(σ²))` with `σ = softplus(ρ)` and samples
`w = μ + σ ⊙ ε`, `ε ~ N(0,I)`. The negative variational free-energy
combines the likelihood term and prior complexity:

`F(q) = KL(q(w) || p(w)) - E_q[log p(D|w)]`.

The implementation samples weights, estimates a scale-mixture-prior complexity
cost, applies a configurable minibatch KL weighting (`equal_minibatch` or
`blundell_geometric`), and separately handles learning rates for means and
`ρ` parameters. There are optional warm-up and variance-floor controls.
Its server representation and aggregation are **not** interchangeable with
FOLA raw mean–precision vectors. BBB is not supported by wireless v2.

**Code:** `training/bbb.py`, `models/bayesian_layers.py`,
`posterior/scale_mixture.py`, `posterior/gaussian.py`.

## C. FOLA — dense Bayesian federated learning (implemented)

The global broadcast is interpreted as a local prior. In the selected
`paper_reference` mode, local weights are optimized using task cross entropy
and a global-precision-weighted quadratic prior term. The round-specific
objective is schematically

`CE(θ; D_k) + λ * (1/(2t)) Σ_i ω_G,t,i * (θ_i - μ_G,t,i)²`.

This is a **MAP-style optimization with a diagonal Laplace/Fisher surrogate**,
not BBB's stochastic variational optimization. The actual source computes
**squared gradients of each minibatch-mean task loss**, accumulating
`(batch_size/n_k) * grad(CE)²` at each minibatch of each local epoch. It starts
its raw local `ω` from the incoming raw precision, adds this surrogate, and
returns the local optimized mean and raw precision. It does not compute
per-example gradients or the exact Hessian.

The source also retains an alternative `online_recurrence` mode with a history
recurrence, precision clipping and optional variance-floor behavior. This
mode is a *distinct implementation option*, not the selected primary
first-submission setting; do not conflate it with `paper_reference`.

The server's weighted diagonal Gaussian product uses each coordinate's
precision. In `paper_reference` mode the actual reducer is:

`ω_G,t+1,i = Σ_k π_k ω_k,t,i`

`μ_G,t+1,i = [Σ_k π_k ω_k,t,i μ_k,t,i] / (ω_G,t+1,i + ε_agg)`.

It retains its existing **epsilon denominator convention** and raw zero
precisions. `online_recurrence` instead uses the clipping-stabilized Gaussian
product in `posterior/gaussian.py`. Both are approximations in the implemented
FOLA framework, not exact inference on all clients' data.

**Code:** `training/fola.py`, `posterior/aggregation.py`,
`posterior/gaussian.py`, `posterior/packing.py`.

## D. Fixed-ratio FedKLS (implemented first submission)

FedKLS leaves C's local training unchanged and compresses only the **uplink
posterior message**. For a coordinate `i`, the primary score is:

`S_k,i = KL[N(μ_G,i, v_G,i) || N(μ_k,i, v_k,i)]`

`      = 0.5 * [log(v_k,i/v_G,i) + (v_G,i + (μ_G,i-μ_k,i)²)/v_k,i - 1]`.

This is the **global-before → local-after** direction. It measures the local
reconstruction penalty under the selected diagonal Gaussian criterion. It is
**not** the direct change in global accuracy. Where a raw precision is zero,
`floor_for_score` can replace it with a strictly positive *scoring-only*
precision; the actual raw trained/uploaded/aggregated tensor is unchanged.
`strict` scoring refuses nonpositive precision.

For `r ∈ (0,1]`, choose `m = ceil(r*d)` highest scores across the **whole
flattened parameter vector**, with ascending coordinate index as the tie
breaker. Build a bitmap and transmit the selected float32 **mean–raw-precision
pairs** in ascending parameter index. `kl_local_global` is a separate,
historically available reverse-KL selector; `random` chooses exactly `m`
coordinates using a dedicated client/round seed. These are selection controls,
not new learning algorithms.

**Critical omitted-coordinate semantics:** For each client and coordinate,

`(μ̃_k,i, ω̃_k,i) = (μ_k,i, ω_k,i)      if the bit is selected`

`               = (μ_G,t,i, ω_G,t,i)   otherwise`.

Aggregate the K **reconstructed full-length** client distributions using C's
same FOLA reducer and normalized sample weights. A coordinate omitted by all
clients is explicitly restored to the prior global values in the current
implementation. There is no zero pruning, `1/r` scaling, or reweighting only
over clients who selected that coordinate.

**Code:** `posterior/sparse.py`, `posterior/packing.py`,
`posterior/aggregation.py`, `strategies/research_strategy.py`.

## E. Communication cost for the first submission

For float32 representations, `d` scalar model weights and `K` full clients,
with one modeled multicast broadcast:

| Method | Modeled **array** bytes per round |
| --- | --- |
| Dense FedAvg | `4*d*(K+1)` |
| Dense FOLA | `8*d*(K+1)` |
| Fixed-ratio sparse FOLA v1 | `8*d + K*(8*ceil(r*d) + ceil(d/8))` |

The v1 sparse packet always includes the bitmap, even at `r=1`; a separate
dense packet does not. This is not measured network framing, MAC traffic or
radio airtime. The selected legacy profiles use a dense FOLA **R150** budget
and a FedAvg **R300** byte-matched endpoint. See [EXPERIMENTS.md](EXPERIMENTS.md).

## F. What the project literature does *not* implement here

The attached project library supports a wider research discussion than the
implemented learner. The following is a **boundary map**, not an assertion
that every paper's algorithm appears in `src/`:

| Provided work | Scientific role | Implemented in FedKLS? |
| --- | --- | --- |
| `00_CommunicationEfficientLearning...` (FedAvg) | Deterministic distributed local SGD + weighted model averaging | **Yes**, FedAvg baseline |
| `01_WeightUncertainty...` (Bayes by Backprop) | VI/Gaussian mean-field weight uncertainty, scale-mixture prior | **Yes**, BBB historical baseline; **not** wireless learner |
| `02_OnlineLaplace...` (FOLA) | Prior iteration, diagonal online curvature, Gaussian-product aggregation | **Yes**, `paper_reference` and optional `online_recurrence` variants |
| `03_FederatedLearningviaVariationalBayesianInference...` (pFedBayes, sFedBayes, cFedBayes) | Personalized, sparse and clustered *variational* Bayesian FL | **No**. These algorithms maintain personalized/cluster-level objectives, not this FOLA protocol |
| `04_BayesianLotteryTicketHypothesis` | Train–prune–reset sparsity in Bayesian neural networks | **No pruning**; only motivates distinction between model sparsity and transmission |
| `05_FederatedDropout` | Client-specific subnet **training**, reconstruction, resource awareness | **No**. FedKLS clients train the full dense model |
| `06_FederatedDropout_ConvergenceAnalysis...` | FedDrop convergence and bandwidth/dropout resource allocation | **No**. Its dropout bound does not establish a FedKLS KL omission bound |
| `00_SchedulingFL` | Channel-and-importance-aware selection of **clients** | **No**. The present wireless protocol assumes all-client participation |
| `07_AirCompWirelessFederatedLearning` | Distribution-level analog superposition of Bayesian sufficient statistics | **No**. FedKLS wireless v2 is reliable digital **orthogonal** transmission |
| `08_PVIFL` | PVI with persistent approximate likelihood/site factors and cavity updates | **No**. FOLA weighted Gaussian products are not PVI cavity updates |
| `bayesian_sparse_survey` | Cautious theory/evidence comparison for sparse posterior **messages** | Research background; not a training component |
| `[Paper]_FedKLS_1stSubmission` | Main KL(global-before||local-after) selection and reconstruction | **Yes**, fixed ratio + random control |
| `FedKLS_Wireless_Develop` | Wireless-resource optimization research proposal | **Implemented with documented adaptations** in wireless v2 |

A successful Bayesian *weight pruning* result cannot establish that omitting
client messages every training round preserves convergence; neither FedDrop's
stochastic subnet argument nor PVI's factor updates should be silently
attributed to the current code. The current wireless implementation is
described in [WIRELESS.md](WIRELESS.md).

## Baseline sequence, in one place

```text
load exact config and partition / validate hash
        ↓
server initialize and broadcast global weights / posterior
        ↓
all chosen clients: deterministic seed + local loader + build model
        ↓
full local SGD (FedAvg) or BBB VI or FOLA MAP+curvature
        ↓
full upload (dense) OR select fixed m by KL/random (FedKLS)
        ↓
validate packet, fill omitted values from the broadcast
        ↓
weighted model average / FOLA Gaussian product
        ↓
central evaluation (mean-only when configured), metric accounting
        ↓
commit completed round and repeat until the declared limit
```
