"""Command line on the synthetic archive."""
from __future__ import annotations

import json

import pytest

from scale_reversal import evidence
from scale_reversal.archive import read_csv
from scale_reversal.cli import main

from test_study import GRID_COLUMNS


def test_cohort_sweep_and_amplified(synthetic_env, tmp_path, capsys):
    assert main(["cohort", "--out", str(tmp_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["cohort"]["windows"] > 0 and report["differences_from_published"]
    assert main(["cohort", "--check"]) == 1
    capsys.readouterr()
    windows = read_csv(tmp_path / "cohort_windows.csv")
    assert len(windows) == report["cohort"]["windows"] and "trees" not in windows[0]
    assert len(read_csv(tmp_path / "cohort_pairs.csv")) == report["cohort"]["pairs"]
    assert main(["sweep", "--out", str(tmp_path)]) == 0
    sweep_report = json.loads(capsys.readouterr().out)["sweep"]
    assert sweep_report["points"] == 45 and len(sweep_report["report_points"]) == 4
    assert list(read_csv(tmp_path / "price_grid.csv")[0]) == GRID_COLUMNS
    assert (tmp_path / "price_grid.csv").read_bytes().count(b"\r\n") == 46
    assert main(["amplified", "--out", str(tmp_path)]) == 0
    aa = json.loads(capsys.readouterr().out)["amplified"]
    assert aa["groups"] == 1 and len(read_csv(tmp_path / "aa_by_source.csv")) == 2
    assert b"\r" not in (tmp_path / "aa_by_source.csv").read_bytes()


def test_missing_evidence(monkeypatch):
    for variable, _ in evidence.ARTEFACTS.values():
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.delenv("SR_EVIDENCE", raising=False)
    with pytest.raises(evidence.EvidenceNotConfigured):
        main(["cohort"])
