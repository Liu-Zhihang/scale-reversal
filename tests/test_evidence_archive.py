"""Evidence locations and readers for the sealed archive layout (synthetic data)."""
from __future__ import annotations

import json

import pytest

import qrq
from scale_reversal import archive, evidence

from synthetic_archive import DAYS, GROUPS


def test_locate_resolution(tmp_path, monkeypatch):
    for variable, _ in evidence.ARTEFACTS.values():
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.delenv("SR_EVIDENCE", raising=False)
    with pytest.raises(evidence.EvidenceNotConfigured):
        evidence.locate("ledgers")
    (tmp_path / evidence.COHORT_RUN / "evidence").mkdir(parents=True)
    monkeypatch.setenv("SR_EVIDENCE", str(tmp_path))
    assert evidence.locate("ledgers") == tmp_path / evidence.COHORT_RUN / "evidence"
    assert evidence.locate("task_archive") == tmp_path
    with pytest.raises(NotADirectoryError):
        evidence.locate("sweep_tables")
    monkeypatch.setenv("SR_SWEEP_TABLES", str(tmp_path))
    assert evidence.locate("sweep_tables") == tmp_path


def test_find_ledger_days(synthetic_archive, tmp_path):
    days = archive.find_ledger_days(synthetic_archive / "ledgers")
    assert [(d.source_id, d.date) for d in days] == sorted((s, d) for s, d, _ in DAYS)
    assert all(list(d.paths) == list(qrq.TREE_KINDS) for d in days)
    broken = tmp_path / "host" / "outputs" / "s" / "d"
    broken.mkdir(parents=True)
    (broken / "kd_tree.jsonl.gz").write_bytes(b"")
    with pytest.raises(ValueError):
        archive.find_ledger_days(tmp_path)


def test_readers(synthetic_archive, tmp_path):
    assert archive.read_groups(synthetic_archive / "tables") == GROUPS
    (tmp_path / "queries").mkdir()
    (tmp_path / "geometry_qa.json").write_text(json.dumps([{"source_id": "s", "reference": {"x": 1.5, "y": 2.5}}]))
    (tmp_path / "queries" / "s.json").write_text(json.dumps([{"query_id": "q"}]))
    assert archive.read_reference_points(tmp_path) == {"s": (1.5, 2.5)}
    assert archive.read_registered_queries(tmp_path, "s") == [{"query_id": "q"}]
