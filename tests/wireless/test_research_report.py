"""Research handoff is read-only and never silently upgrades incomplete evidence."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from bayesfl.wireless.research_report import analyze_run, export_zip, report_markdown
from bayesfl.wireless.smoke import smoke_config, run_smoke

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def finished_run(tmp_path):
    directory = tmp_path / "smoke_wireless_joint_kl"
    run_smoke(smoke_config(rounds=2), directory)
    return directory


def test_strict_report_rounds_kl_and_no_source_changes(finished_run):
    csv_path = finished_run / "metrics/wireless_clients.csv"
    original = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    result = analyze_run(finished_run)
    assert result["completed_rounds"] == 2
    assert result["validation_scope"] == "recorded_metrics_and_raw_checkpoint_digests"
    assert result["checkpoint_integrity"]["status"] == "verified_byte_digests"
    assert len(result["rounds"]) == 2
    assert result["clients"] == 3
    assert all(0 < row["mean_keep_ratio"] <= 1 for row in result["rounds"])
    assert all(row["weighted_discarded_kl"] >= 0 for row in result["rounds"])
    assert "not" in report_markdown([result]).lower()
    assert hashlib.sha256(csv_path.read_bytes()).hexdigest() == original


def test_state_digest_corruption_is_not_ignored(finished_run):
    latest = json.loads((finished_run / "wireless_resume/latest.json").read_text())
    state_path = finished_run / "wireless_resume" / latest["state_file"]
    state_path.write_bytes(state_path.read_bytes().replace(b"\n", b"\r\n"))
    with pytest.raises(ValueError, match="hash|digest|checkpoint|Checkpoint"):
        analyze_run(finished_run)
    downgraded = analyze_run(finished_run, records_only=True)
    assert downgraded["validation_scope"] == "records_only_unverified_checkpoint"
    assert downgraded["checkpoint_integrity"]["status"] == "inconsistent"
    assert any("state JSON" in s for s in downgraded["checkpoint_integrity"]["issues"])


def test_records_only_still_checks_statistical_accounting(finished_run):
    path = finished_run / "metrics/wireless_clients.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    rows[0]["actual_discarded_kl"] = str(float(rows[0]["actual_discarded_kl"]) + 1000)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="Sample-weighted discarded KL mismatch"):
        analyze_run(finished_run, records_only=True)


def test_portable_zip_contains_evidence_not_model_states(finished_run, tmp_path):
    path = tmp_path / "handoff.zip"
    records = export_zip([finished_run], path)
    assert records[0]["completed_rounds"] == 2
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        assert "RESEARCH_REPORT.md" in names and "RESEARCH_REPORT.json" in names
        assert f"evidence/{finished_run.name}/metrics/wireless_clients.csv" in names
        assert not any(".npz" in s or "events.jsonl" in s or "wireless_resume" in s for s in names)
        manifest = json.loads(archive.read("HANDOFF_HASHES.json"))
        for entry in manifest:
            data = archive.read(entry["file"])
            assert entry["bytes"] == len(data)
            assert entry["sha256"] == hashlib.sha256(data).hexdigest()
        info = json.loads(archive.read("RESEARCH_REPORT.json"))
        assert info["schema"] == "fedkls-wireless-research-v1"
    with pytest.raises(FileExistsError):
        export_zip([finished_run], path)
    with pytest.raises(ValueError, match="protected run"):
        export_zip([finished_run], finished_run / "report.zip")


def test_cli_check_does_not_write_reports(finished_run):
    command = [sys.executable, str(ROOT / "scripts/export_research_report.py"),
               "--run-dir", str(finished_run)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "R2" in result.stdout and "checkpoint=verified_byte_digests" in result.stdout
    assert not (finished_run / "report.zip").exists()


def test_report_directory_is_inside_reports_and_never_overwrites(finished_run, tmp_path):
    from bayesfl.wireless.research_report import export_directory
    repo = tmp_path / "repo"
    (repo / "reports").mkdir(parents=True)
    target = repo / "reports" / "report_example"
    originals = {n: hashlib.sha256((finished_run / n).read_bytes()).hexdigest()
                 for n in ("metrics/global_metrics.csv", "metrics/wireless_rounds.csv",
                           "metrics/wireless_clients.csv")}
    result = export_directory([finished_run], target, repository_root=repo)
    assert len(result) == 1
    assert (target / "RESEARCH_REPORT.md").is_file()
    assert (target / "RESEARCH_REPORT.json").is_file()
    assert (target / "HANDOFF_HASHES.json").is_file()
    assert (target / "research_bundle.zip").is_file()
    assert (target / "evidence" / finished_run.name / "metrics" / "wireless_clients.csv").is_file()
    with zipfile.ZipFile(target / "research_bundle.zip") as zipped:
        assert zipped.testzip() is None
        assert "RESEARCH_REPORT.md" in zipped.namelist()
    assert originals == {n: hashlib.sha256((finished_run / n).read_bytes()).hexdigest()
                         for n in originals}
    with pytest.raises(FileExistsError):
        export_directory([finished_run], target, repository_root=repo)
    with pytest.raises(ValueError, match="direct reports"):
        export_directory([finished_run], finished_run / "report_bad", repository_root=repo)


def test_report_cli_requires_write_for_custom_label(tmp_path):
    script = ROOT / "scripts" / "export_research_report.py"
    proc = subprocess.run([sys.executable, str(script), "--run-dir", str(tmp_path),
                           "--report-name", "sample"], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "requires --write-report" in proc.stderr
