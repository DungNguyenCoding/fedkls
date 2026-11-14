# Wireless FedKLS — complete system model and training sequence

This is the implemented **opt-in** `fedkls_wireless_integer_precision_v2`
protocol. It starts from the same FOLA dense local training and posterior-KL
selection as the legacy code, but turns a fixed keep ratio into **per-client
integer retention and bandwidth allocation**. The reference proposal is
under [`wireless/proposal/`](wireless/proposal/); this page documents what the
*source actually implements*, including adaptations.

## 1. Scope and feature boundary

- One server and **all `K` clients** in each synchronous round.
- Model broadcast: one dense global posterior multicast, shared clock modeled
  by the worst downlink channel; no sparse/conditional downlink.
- Each client trains its **complete** local FOLA model once, then caches full
  posterior/scoring data *locally* while the server selects packet sizes.
- Server sees authenticated scalar count/price replies, never the full score
  array or unselected local posterior. It sends exact grants, and clients
  transmit only granted float32 mean/raw-precision values plus bitmap if sparse.
- Orthogonal **digital** channels with successful decode; no waveform
  superposition, quantization beyond float32, fading noise injected into
  coordinates, retransmission, client dropout, privacy mechanism, adaptive
  epochs or power-control optimizer.
- Fixed uplink **PSD** is the physical assumption used for the allocator.
  A fixed-total-power/SNR-dependent bandwidth model would require re-deriving
  the resource constraint; it is not this implementation.

These constraints distinguish FedKLS from AirComp, FedDrop and conventional
importance-aware user scheduling. See [ALGORITHMS.md](ALGORITHMS.md).

## 2. Round sequence — from global prior to durable checkpoint

```text
SERVER                       CLIENT k (each k = 0...K-1)
  │                               │
  ├─ load round t global (μ,ω) ────►│ use global as local FOLA prior
  │        PREPARE                ├─ local data + full dense training ONCE
  │                               ├─ local posterior (μ_k, raw ω_k)
  │                               ├─ KL(global-before || local-after) all d
  │                               └─ sort/cache indices; reverse KL tails D_k(m)
  │        QUERY                  │
  ├─ count/price request ─────────►│ evaluate D_k(m) or local price argmin
  ◄─ scalar count + tail ──────────┤ NO retraining, NO score vector uploaded
  │                               │
  ├─ compute integer grants m_k, allocated bandwidth b_k
  │        GRANT                  │
  ├─ grant(count, channel, digest) ►│ select exactly granted indices
  │                               ├─ encode bitmap + μ_k[selected] + ω_k[selected]
  ◄──────── UPLOAD bytes ──────────┤
  │ validate exact grant, IDs, layout, snapshot and payload bytes
  │ reconstruct each client: omitted coordinates = t's broadcast
  │ RELEASE prepared state  ─────►│ clear cached local posterior / scores
  │ weighted FOLA Gaussian-product aggregation
  │ central evaluation, all-client accuracy/NLL
  │ write metrics, channel/allocation events and raw state
  │ commit evaluated round + checksums, update time/byte budget
  └─ repeat or stop after complete fixed slot
```

Client-owned prepared state is retained across ephemeral Flower client objects
using `Context.state` or an explicit memory store in the local emulator. Every
round binds the snapshot, layout, protocol, client ID, round ID and run token.
Separate `wireless_resume/` checkpoints prevent accidental mixing with legacy
byte-budget resume. An interrupted round does not become a completed data row.

**Source trace:** `wireless/runner.py` → `controller.py` → `client.py` and
`transport.py` → `oracle.py`, `allocation.py` → `protocol.py` →
`posterior/aggregation.py` → `wireless/state.py` and `evaluation.py`.

## 3. Score state and reconstruction objective

At client `k` create stable scores `s_k,i` according to the FOLA posterior
changes. Sort by **descending** score then ascending original coordinate
index. Define the omitted-tail cost for sending top `m` updates:

`D_k(m) = Σ_{i not in top-m} s_k,i`.

The source uses reverse cumulative tails (rather than subtracting nearly
equal total and prefix sums) and supports any integer `m ∈ {1,...,d}`. A
count request returns `D_k(m)`; a price request returns an integer count and
its tail. This is a client-side scalar oracle, not transmission of scores.

At the server minimize the **sample-weighted** reconstruction surrogate:

`min_{m_1,...,m_K}  Σ_k π_k D_k(m_k)`.

The criterion measures omission in coordinate Gaussian KL, **not** expected
global test loss; `random` selection can use the same allocated counts but
has a larger *actual* discarded score than the corresponding top-m prefix.

## 4. Precise v2 payload and packet representation

For float32 means/precisions, integer `m` and total dimension `d`:

| Packet format | Uplink payload bytes |
| --- | --- |
| FOLA sparse `1 <= m < d` | `8*m + ceil(d/8)` |
| FOLA dense `m = d` | `8*d` (no bitmap) |
| FedAvg dense | `4*d` (mean only) |

The bitmap is packed by bytes, including padding; trailing padding bits must
be zero. Selected pairs are serialized in **ascending parameter index**, not
importance rank. An upload grant records exact `m`, intended payload bytes,
channel and signed digest. Decoder validates counts/shapes/dtypes/IDs,
restores omitted raw `(μ,ω)` values from the immutable broadcast, then
invokes the original normalized-sample FOLA reducer. If all clients omit a
coordinate, the aggregated result is explicitly reset to the broadcast.
The legacy v1 sparse bitmap format remains unchanged.

## 5. Channel and fixed-slot timing model

For each client `k`, the configured linear uplink channel gain `g_k`, fixed
transmit PSD `p_k` (W/Hz), and noise PSD `N0` yield a bandwidth-independent
spectral efficiency:

`c_k = log2(1 + p_k*g_k/N0)` (bits/s/Hz).

For a shared upload window `U` and bandwidth `b_k`, an integer-packet upload
is feasible only if `L(m_k) <= U*b_k*c_k` bits. Eliminating the per-client
bandwidth variables for the minimum necessary allocation yields:

`Σ_k L(m_k) / (U*c_k) <= B_max`, with `m_k ∈ {1,...,d}`.

`L(m)=8*payload_bytes(m)` includes padded bitmap and the dense-format switch.
One cannot drop the bitmap cost or relax integer counts into a continuous
keep-ratio fraction when applying this formula.

The modeled round begins with one dense multicast downlink. The downlink
rate is limited by the minimum downlink client efficiency. Per-client model
preparation time is explicitly specified as

`prep_k = n_k*E*seconds_per_sample_epoch_k + fixed_seconds_k + score_seconds_k`.

The controller computes the **shared** upload window

`U = round_target_s - DL_time - max_k(prep_k) - control_reserve_s`.

Control uses canonical UTF-8 JSON lengths at one explicit shared logical
control service rate plus per-exchange latency. The real control time must
fit the reserved interval; unused reservation is counted as idle. The
successful upload time must fit `U`, and the **modeled total round still
occupies the full declared fixed slot**, even if packets finish early.
Emulator GPU/RPC/wall seconds are logged separately: no physical sleeping is
simulated to realize the modeled deadline.

Fixed channel gains, counter-seeded block-Rayleigh fading and exact per-round
CSV traces are supported. Trace mode requires all `(round, client)` pairs;
duplicate/missing entries fail, and the pinned trace hash is checked on resume.
A conservative client power cap can be declared, but the default solver
is **not** a general power allocator.

## 6. Allocation policies and numerical limits

- `joint` (primary research policy): client price oracle compares
  `π_k D_k(m) + p*L(m)/(U*c_k)` including dense packet as an explicit
  alternative. Server brackets and bisects price; it maintains minimum
  feasible and equal-share incumbents, validates all returned grants, and
  retains the best feasible integer allocation found. Floating numerical
  primal/dual gap diagnostics do **not** certify global integer optimality.
- `equal_bandwidth`: each client receives `B_max/K`, chooses its maximum
  feasible integer count, and waits for the common slot boundary.
- `uniform`: feasible equal-bandwidth counts are computed, then each client
  receives the minimum of those counts, for a uniform retention baseline.
- `dense`: each client sends all coordinates; it must actually fit the same
  resource constraints. Dense FOLA and dense FedAvg use distinct payload sizes.

Selection can be `kl_global_local` or `random` for adaptive FOLA; the joint
allocation for the random control is driven by its own current KL oracle but
randomly selects which positions are transmitted at the granted count. Equal
counts at one round do **not** imply equal later training trajectories.

If even a minimal all-client message is infeasible, or dense comparator cannot
fit the requested scenario, the system reports a failure. It does not widen
resources, shorten training or suppress a client to make a comparison run.
The joint price search is *not an exhaustive global integer solver*.

## 7. Configurations, bytes, time and energy

`wireless.enabled` is opt-in; when false, the legacy serialized config and
its fingerprint remain unchanged. The main YAML fields are:

| Group | Fields / meaning |
| --- | --- |
| Core | `backend` (`flower` / `local`), `policy`, `uplink_bandwidth_hz`, `downlink_bandwidth_hz`, `round_target_s`, optional `total_time_budget_s` |
| Control | `control_reserve_s`, `control_rate_bps`, `control_exchange_latency_s`, `rpc_timeout_s` (RPC timeout is host wall clock, not radio time) |
| Channel | `mode` (`fixed`, `block_rayleigh`, `trace`), `seed`, `path_gains`, `uplink_psd_w_hz`, `downlink_psd_w_hz`, `noise_psd_w_hz`, `reciprocal_fading`, optional trace and conservative caps |
| Compute | Per-client `seconds_per_sample_epoch`, `fixed_seconds`, `score_seconds` |
| Solver | Price initialization, max bracket/bisection queries, price/gap tolerances |

All vectors must match exact logical client count, and positivity/finite
conditions are validated. For FOLA dynamic selection, keep ratio is a **1.0
placeholder** and has no effect on the returned integer grant. All clients
participate, epochs `<=10`, no server-side full-client posterior snapshots,
multicast downlink, and no simultaneous legacy fixed-byte stop cap.
See `scripts/configs/wireless/scenario_example.yaml` for syntax, but
**`EXAMPLE_NOT_LOCKED` means it is not a calibrated or approved paper setting**.

The system records **four different quantities**:

1. model array bytes: one dense multicast plus each exact received packet;
2. logical control JSON bytes: separate from model arrays (not actual PHY frames);
3. modeled fixed-slot seconds: not measured host/GPU execution duration;
4. modeled UL+DL data-plane energy (PSD × granted bandwidth × airtime),
   **excluding** compute, circuit, control and idle energy.

These should never be summed into a single vaguely named “communication cost.”

## 8. Source-backed deviations from the original proposal

The proposal used abstract posterior mean/variance and idealized bitmap/cost
formulations. The implemented protocol instead sends **float32 mean/raw
precision**, floors only for KL *scoring* when needed, counts byte-padded
bitmaps, switches to no-bitmap dense packets, reserves modeled control time,
uses fixed slots, and reports numerical (not certified) optimizer gaps. These
are engineering/scientific assumptions; they are not automatically claims
made by the proposal itself.

**Not included:** AirComp, SNR recalculation from fixed total power when
bandwidth changes, interference, errors/retries, stochastic packet loss,
sparse local compute/downlink, client scheduling, personalized or PVI factor
updates, actual RF profiling, and calibrated energy/carbon accounting.
