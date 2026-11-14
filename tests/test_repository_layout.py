"""Only active science docs are in the entrypoint; historical text remains audited."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_active_docs_are_small_indexed_and_archived():
    assert {p.name for p in ROOT.glob("*.md")} == {"README.md", "AGENTS.md"}
    for name in ("ARCHITECTURE.md", "ALGORITHMS.md", "WIRELESS.md",
                 "EXPERIMENTS.md", "RESULTS.md", "REPRODUCIBILITY.md",
                 "ARCHIVE_INDEX.md", "README.md"):
        assert (ROOT / "docs" / name).is_file(), name
    assert (ROOT / "reports" / "README.md").is_file()
    assert (ROOT / "reports" / "REPORT_TEMPLATE.md").is_file()
    assert not (ROOT / "backups").exists()
    assert not (ROOT / "modified_source").exists()
    assert not list(ROOT.glob("*.json"))
    assert [p.name for p in ROOT.glob("*.txt")] == ["requirements.txt"]
    assert not list((ROOT / "src").rglob("*.before_*"))


def test_relocated_historical_docs_are_byte_preserved():
    archive = ROOT / "docs/archive/2026-11-12-snapshot"
    manifest = json.loads((archive / "RELOCATION_MAP.json").read_text())
    for record in manifest["moved_files"]:
        path = ROOT / record["to"]
        assert path.is_file(), record["to"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    for key in ("docs/CHAT_HANDOFF.md", "docs/LOCKED_EXPERIMENTS.md",
                "docs/wireless/JOINT_CIFAR10_SENSITIVITY_R150_20261112.md",
                "docs/wireless/r150_joint_20261110/JOINT_R150_REVIEW.md"):
        assert (archive / key).is_file()
