"""Read-only, auditable research reports for completed wireless-v2 runs.

The output is a *recorded-evidence handoff*, not a checkpoint, training backup,
causal analysis, or claim that the integer allocator is globally optimal.
Standard library only; importing this module does not load Torch or Flower.
"""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import stat
import subprocess
import shutil
import uuid
import zipfile

from bayesfl.wireless.reporting import inspect_run

SCHEMA_VERSION = "fedkls-wireless-research-v1"
REQUIRED_FILES = (
    "resolved_config.yaml",
    "run_summary.json",
    "wireless/protocol.json",
    "wireless/layout_manifest.json",
    "metrics/global_metrics.csv",
    "metrics/wireless_rounds.csv",
    "metrics/wireless_clients.csv",
)
OPTIONAL_FILES = (
    "source_config.yaml", "partition_metadata.json", "environment.json",
    "wireless/channel_trace.csv",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_read(path: Path) -> bytes:
    """Refuse symlinks and reads of files actively modified by a writer."""
    if path.is_symlink():
        raise ValueError(f"Refusing symbolic input: {path}")
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Not a regular file: {path}")
    data = path.read_bytes()
    after = path.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_ino, after.st_size, after.st_mtime_ns
    ):
        raise ValueError(f"Input changed during export: {path}")
    return data


def _read_csv(run_dir: Path, rel: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(_stable_read(run_dir / rel).decode("utf-8-sig"))))


def _number(row: dict, key: str) -> float:
    try:
        value = float(row[key])
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError(f"Missing or invalid {key} in recorded metrics") from exc
    if not math.isfinite(value):
        raise ValueError(f"Nonfinite {key} in recorded metrics")
    return value


def _whole(row: dict, key: str) -> int:
    value = _number(row, key)
    if value != int(value):
        raise ValueError(f"Noninteger {key} in recorded metrics")
    return int(value)


def _safe_name(name: str) -> str:
    path = Path(name)
    if not name or path.name != name or name in (".", ".."):
        raise ValueError(f"Unsafe checkpoint filename: {name!r}")
    return name


def _integrity(run_dir: Path, completed_rounds: int) -> dict:
    """Verify raw byte digests; NEVER normalize line endings or rewrite expected hashes."""
    latest = run_dir / "wireless_resume/latest.json"
    issues = []
    checked = []
    if not latest.is_file():
        return {"status": "absent", "verified": [], "issues": ["No wireless_resume/latest.json"]}
    try:
        latest_data = json.loads(_stable_read(latest))
        state_path = latest.parent / _safe_name(latest_data["state_file"])
        if _sha256(state_path) != latest_data["state_sha256"]:
            issues.append("Checkpoint state JSON raw SHA-256 mismatch")
        else:
            checked.append("state_json")
        state = json.loads(_stable_read(state_path))
        if int(state["round_id"]) != completed_rounds:
            issues.append("Latest checkpoint round differs from last evaluated round")
        else:
            checked.append("checkpoint_round")
        arrays_path = latest.parent / _safe_name(state["arrays_file"])
        if _sha256(arrays_path) != state["arrays_sha256"]:
            issues.append("Checkpoint array raw SHA-256 mismatch")
        else:
            checked.append("checkpoint_arrays_bytes")
        events = run_dir / "wireless/events.jsonl"
        if _sha256(events) != state["events_sha256"]:
            issues.append("Event ledger raw SHA-256 mismatch")
        else:
            checked.append("event_ledger_bytes")
        for rel, expected in state["tracked_sha256"].items():
            path = Path(rel)
            if path.is_absolute() or ".." in path.parts or not rel.startswith("metrics/"):
                issues.append(f"Unsafe tracked metrics path: {rel!r}")
                continue
            if _sha256(run_dir / path) != expected:
                issues.append(f"Tracked metric raw SHA-256 mismatch: {rel}")
            else:
                checked.append(rel)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        issues.append(f"Cannot verify checkpoint bytes: {type(exc).__name__}: {exc}")
    return {"status": "verified_byte_digests" if not issues else "inconsistent",
            "verified": checked, "issues": issues}


def analyze_run(run_dir: Path, *, records_only: bool = False) -> dict:
    """Inspect one completed run; strict mode refuses incompatible checkpoint bytes.

    records_only=True is a deliberate downgrade for transformed archive copies:
    metrics are checked, but state/ledger problems are reported rather than ignored.
    Such a report must not be used to authorize resume or claim full integrity.
    """
    run_dir = Path(run_dir).expanduser().resolve(strict=True)
    inspected = inspect_run(run_dir, verify_checkpoint=not records_only)
    last = inspected["completed_rounds"]
    integrity = _integrity(run_dir, last)
    if not records_only and integrity["status"] != "verified_byte_digests":
        raise ValueError("Research export requires intact checkpoint/ledger bytes: " +
                         "; ".join(integrity["issues"]))
    global_rows = _read_csv(run_dir, "metrics/global_metrics.csv")
    round_rows = _read_csv(run_dir, "metrics/wireless_rounds.csv")
    client_rows = _read_csv(run_dir, "metrics/wireless_clients.csv")
    d = _whole(json.loads(_stable_read(run_dir / "wireless/layout_manifest.json")), "d")
    k = _whole(json.loads(_stable_read(run_dir / "wireless/protocol.json")), "num_clients")
    by_round: dict[int, list[dict]] = {r: [] for r in range(1, last + 1)}
    sizes: dict[int, int] = {}
    for client in client_rows:
        r, cid = _whole(client, "round"), _whole(client, "client_id")
        if r not in by_round or cid not in range(k):
            raise ValueError("Invalid recorded round/client identifier")
        n = _whole(client, "num_examples")
        if n <= 0 or (cid in sizes and sizes[cid] != n):
            raise ValueError("Client sample counts must be positive and fixed across rounds")
        sizes[cid] = n
        by_round[r].append(client)
    if len(sizes) != k:
        raise ValueError("Missing client sample-count evidence")
    total_samples = sum(sizes.values())
    timeseries = []
    statuses = Counter()
    accuracies = []
    for r, rr in enumerate(round_rows, start=1):
        clients = by_round[r]
        if len(clients) != k:
            raise ValueError(f"Missing/duplicate clients in round {r}")
        weighted_kl = math.fsum(sizes[_whole(c, "client_id")] / total_samples *
                                _number(c, "actual_discarded_kl") for c in clients)
        logged_kl = _number(rr, "actual_reconstruction_objective")
        if not math.isclose(weighted_kl, logged_kl, abs_tol=1e-6, rel_tol=1e-8):
            raise ValueError(f"Sample-weighted discarded KL mismatch in round {r}")
        for client in clients:
            cid = _whole(client, "client_id")
            expected_weight = sizes[cid] / total_samples
            if not math.isclose(_number(client, "weight"), expected_weight,
                                abs_tol=1e-10, rel_tol=1e-8):
                raise ValueError(f"Incorrect normalized client weight at R{r}/C{cid}")
        actual_keep = math.fsum(_whole(c, "keep_count") for c in clients) / (k * d)
        if not math.isclose(actual_keep, _number(rr, "mean_keep_ratio"), abs_tol=1e-9, rel_tol=1e-8):
            raise ValueError(f"Mean retained fraction mismatch at R{r}")
        g = global_rows[r]
        key = "fola_mean_accuracy" if inspected["method"] == "fola" else "accuracy"
        accuracy = _number(g, key) * 100
        if not 0 <= accuracy <= 100:
            raise ValueError(f"Invalid recorded accuracy at R{r}")
        statuses[rr["allocation_status"]] += 1
        timeseries.append({
            "round": r,
            "accuracy_percent": accuracy,
            "nll": _number(g, "fola_mean_nll" if inspected["method"] == "fola" and
                           g.get("fola_mean_nll") not in (None, "") else "nll"),
            "mean_keep_ratio": actual_keep,
            "weighted_discarded_kl": weighted_kl,
            "price_queries": _whole(rr, "price_queries"),
            "allocation_status": rr["allocation_status"],
            "cumulative_array_bytes": _whole(g, "cumulative_all_array_bytes"),
            "cumulative_control_bytes": _whole(g, "cumulative_control_bytes"),
            "cumulative_modeled_time_seconds": _number(g, "cumulative_modeled_time_seconds"),
        })
        accuracies.append(accuracy)
    drops = sorted(({"round": r + 1,
                     "accuracy_drop_pp": accuracies[r - 1] - accuracies[r],
                     "before_percent": accuracies[r - 1],
                     "after_percent": accuracies[r]}
                    for r in range(1, len(accuracies))
                    if accuracies[r] < accuracies[r - 1]),
                   key=lambda x: (-x["accuracy_drop_pp"], x["round"]))[:5]
    if not math.isclose(accuracies[-1], inspected["accuracy_percent"], abs_tol=1e-9):
        raise ValueError("Computed final accuracy differs from inspection")
    return {
        "schema": SCHEMA_VERSION,
        "run": run_dir.name,
        "validation_scope": "records_only_unverified_checkpoint" if records_only else
                            "recorded_metrics_and_raw_checkpoint_digests",
        "checkpoint_integrity": integrity,
        "method": inspected["method"],
        "policy": inspected["policy"],
        "selector": inspected["selection_rule"],
        "clients": k,
        "parameters": d,
        "completed_rounds": last,
        "final_accuracy_percent": accuracies[-1],
        "best_accuracy_percent": max(accuracies),
        "best_accuracy_round": accuracies.index(max(accuracies)) + 1,
        "final_nll": timeseries[-1]["nll"],
        "final_mean_keep_ratio": timeseries[-1]["mean_keep_ratio"],
        "cumulative_array_bytes": timeseries[-1]["cumulative_array_bytes"],
        "cumulative_control_bytes": timeseries[-1]["cumulative_control_bytes"],
        "cumulative_modeled_time_seconds": timeseries[-1]["cumulative_modeled_time_seconds"],
        "allocation_status_counts": dict(sorted(statuses.items())),
        "largest_single_round_accuracy_drops": drops,
        "rounds": timeseries,
        "input_hashes": inspected["input_hashes"],
        "interpretation_limits": [
            "Measurements are recorded simulation metrics, not independently rerun training.",
            "Wireless time and transmit energy are modeled, not measured wall time or RF measurements.",
            "Discarded KL is an omission proxy, not accuracy loss or proven cause of oscillation.",
            "The solver's objective gap is numerical; global integer optimality is not certified.",
            "Do not compare scenario endpoints as equal modeled time unless times actually match.",
            "A result bundle contains no checkpoint tensors or full event ledger and cannot resume training.",
        ],
    }


def report_markdown(runs: list[dict]) -> str:
    lines = ["# FedKLS wireless research handoff", "",
             "This report describes **saved experimental records**, not freshly executed training.",
             "No conclusions about causality, statistical significance or global solver optimality are implied.", "",
             "| Run | Rounds | Accuracy (%) | Final keep (%) | Array GB | Modeled h | State integrity |",
             "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for r in runs:
        lines.append(f"| {r['run']} | {r['completed_rounds']} | {r['final_accuracy_percent']:.3f} | "
                     f"{100*r['final_mean_keep_ratio']:.2f} | {r['cumulative_array_bytes']/1e9:.6f} | "
                     f"{r['cumulative_modeled_time_seconds']/3600:.4f} | {r['checkpoint_integrity']['status']} |")
    if len(runs) > 1:
        same = all(math.isclose(r["cumulative_modeled_time_seconds"], runs[0]["cumulative_modeled_time_seconds"],
                                abs_tol=1e-6, rel_tol=1e-10) for r in runs)
        lines.extend(["", "**Comparison caution:** " +
                      ("Endpoints have equal recorded modeled time; training/partitions/scenario still require review."
                       if same else "Endpoints have **different recorded modeled times**; do not claim an equal-time comparison."), ""])
    for r in runs:
        lines.extend(["", f"## {r['run']}", "",
                      f"- Completed R{r['completed_rounds']}; final global test accuracy {r['final_accuracy_percent']:.3f}%, "
                      f"best recorded accuracy {r['best_accuracy_percent']:.3f}% at R{r['best_accuracy_round']}.",
                      f"- Final NLL {r['final_nll']:.6g}, mean keep {100*r['final_mean_keep_ratio']:.2f}%; "
                      f"model-array bytes {r['cumulative_array_bytes']:,}, logical control bytes {r['cumulative_control_bytes']:,}.",
                      f"- Allocation statuses: {json.dumps(r['allocation_status_counts'], sort_keys=True)}.",
                      f"- Evidence scope: `{r['validation_scope']}`; state/ledger digest status: "
                      f"`{r['checkpoint_integrity']['status']}`."])
        for issue in r["checkpoint_integrity"]["issues"]:
            lines.append(f"  - Integrity issue: {issue}")
        if r["largest_single_round_accuracy_drops"]:
            lines.append("- Largest observed consecutive-round accuracy drops (diagnostic; not causal): " +
                         ", ".join(f"R{x['round']} ({x['accuracy_drop_pp']:.3f} pp)"
                                   for x in r["largest_single_round_accuracy_drops"]))
    lines.extend(["", "## How to use this handoff", "",
                  "The ZIP also includes the raw three metrics CSVs, resolved config, protocol and hashes for each run.",
                  "Inspect round-by-round values before attributing accuracy changes to allocation behavior.",
                  "R1 discarded KL may have a very different scale if score-only precision flooring is active.",
                  "This is **not** a safe resume archive: obtain the original verified checkpoint and ledger separately.", ""])
    return "\n".join(lines)


def _git_commit(root: Path | None) -> str | None:
    if root is None or not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                capture_output=True, check=True, text=True, timeout=5)
        return result.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def export_zip(run_dirs: list[Path], output_zip: Path, *, records_only: bool = False,
               repository_root: Path | None = None) -> list[dict]:
    """Write exactly one new lightweight ZIP; never write to a run or overwrite a file."""
    if not run_dirs:
        raise ValueError("At least one explicitly selected run is required")
    directories = [Path(p).expanduser().resolve(strict=True) for p in run_dirs]
    if len(set(directories)) != len(directories) or len({p.name for p in directories}) != len(directories):
        raise ValueError("Duplicate run directory or duplicate run name")
    dest = Path(output_zip).expanduser().resolve(strict=False)
    if dest.suffix.lower() != ".zip":
        raise ValueError("Research handoff output must be a .zip file")
    if dest.exists() or not dest.parent.is_dir():
        raise FileExistsError("Output ZIP exists or output parent directory does not exist")
    for root in directories:
        if dest.is_relative_to(root):
            raise ValueError("Refusing to write a report inside a protected run directory")
    runs = [analyze_run(d, records_only=records_only) for d in directories]
    snapshot: dict[str, bytes] = {}
    manifest: list[dict] = []
    for d, run in zip(directories, runs):
        for rel in REQUIRED_FILES + OPTIONAL_FILES:
            path = d / rel
            if rel in OPTIONAL_FILES and not path.exists():
                continue
            content = _stable_read(path)
            name = f"evidence/{d.name}/{rel}"
            snapshot[name] = content
            digest = hashlib.sha256(content).hexdigest()
            if rel in run["input_hashes"] and digest != run["input_hashes"][rel]:
                raise ValueError(f"Input changed since its run was inspected: {d.name}/{rel}")
            manifest.append({"file": name, "sha256": digest, "bytes": len(content)})
    overall = {
        "schema": SCHEMA_VERSION,
        "git_commit_at_export": _git_commit(repository_root),
        "report_scope": "records_only_unverified_checkpoint" if records_only else
                        "recorded_metrics_and_raw_checkpoint_digests",
        "runs": runs,
        "warning": "No weights, full event ledgers, or training data. Not a training/resume backup.",
    }
    snapshot["RESEARCH_REPORT.json"] = (json.dumps(overall, indent=2, allow_nan=False) + "\n").encode()
    snapshot["RESEARCH_REPORT.md"] = report_markdown(runs).encode()
    manifest.extend({"file": name, "sha256": hashlib.sha256(snapshot[name]).hexdigest(),
                     "bytes": len(snapshot[name])} for name in ("RESEARCH_REPORT.json", "RESEARCH_REPORT.md"))
    snapshot["HANDOFF_HASHES.json"] = (json.dumps(sorted(manifest, key=lambda row: row["file"]), indent=2) + "\n").encode()
    # Build off disk before claiming a destination name. The selected source runs are never opened for writing.
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(snapshot.items()):
            archive.writestr(name, data)
    with dest.open("xb") as stream:
        stream.write(buffer.getvalue())
    with zipfile.ZipFile(dest) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Created ZIP failed CRC validation")
    return runs


def export_directory(run_dirs: list[Path], output_dir: Path, *, records_only: bool = False,
                     repository_root: Path) -> list[dict]:
    """Create one NEW analysis report inside <repository>/reports/, never in outputs.

    Writes a readable report, machine-readable report, hash manifest, copied
    lightweight evidence, and a portable ZIP with identical contents.
    The result is NOT a checkpoint/resume backup.
    """
    repo = Path(repository_root).expanduser().resolve(strict=True)
    reports_root = repo / "reports"
    if not reports_root.is_dir() or reports_root.is_symlink():
        raise ValueError("Repository reports/ must exist and must not be a symlink")
    target = Path(output_dir).expanduser().resolve(strict=False)
    if target.parent != reports_root or not target.name.startswith("report_"):
        raise ValueError("Analysis report must be a direct reports/report_<name> directory")
    if target.exists():
        raise FileExistsError(f"Research report already exists: {target}")
    temporary = reports_root / (".tmp_report_" + uuid.uuid4().hex)
    temporary.mkdir(mode=0o700)
    try:
        path = temporary / "research_bundle.zip"
        runs = export_zip(run_dirs, path, records_only=records_only, repository_root=repo)
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                file = Path(name)
                if file.is_absolute() or ".." in file.parts:
                    raise ValueError("Unsafe generated research bundle member")
                dest = temporary / file
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open("xb") as stream:
                    stream.write(archive.read(name))
        # Atomic directory publication on the same filesystem; the selected
        # raw runs have never been opened for writing.
        temporary.rename(target)
        return runs
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
