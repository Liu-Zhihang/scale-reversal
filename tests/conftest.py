"""Shared fixtures: a synthetic archive and the sealed evidence.

Synthetic fixtures need no data. Sealed fixtures find the sealed evidence
through ``SR_EVIDENCE`` (or the artefact variables of
:mod:`scale_reversal.evidence`) and skip their tests when it is not
configured; see docs/reproduction.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scale_reversal.archive import read_groups
from scale_reversal.cohort import reproduce

from compare import artefact
from synthetic_archive import write_archive


@pytest.fixture(scope="session")
def synthetic_archive(tmp_path_factory) -> Path:
    """Root of the synthetic archive (``ledgers/`` and ``tables/``)."""
    return write_archive(tmp_path_factory.mktemp("archive"))


@pytest.fixture(scope="session")
def synthetic_cohorts(synthetic_archive):
    """First-witness and AA-inclusive cohorts of the synthetic archive."""
    ledgers = synthetic_archive / "ledgers"
    return reproduce(ledgers), reproduce(ledgers, amplified=True)


@pytest.fixture
def synthetic_env(synthetic_archive, monkeypatch) -> Path:
    """Point the artefact variables to the synthetic archive."""
    monkeypatch.setenv("SR_LEDGERS", str(synthetic_archive / "ledgers"))
    monkeypatch.setenv("SR_COHORT_TABLES", str(synthetic_archive / "tables"))
    return synthetic_archive


@pytest.fixture(scope="session")
def sealed_reproduction():
    """Full re-pricing of the sealed ledgers, computed once per session."""
    return reproduce(artefact("ledgers"))


@pytest.fixture(scope="session")
def sealed_amplified():
    """AA-inclusive re-enveloping of the sealed ledgers, computed once per session."""
    return reproduce(artefact("ledgers"), amplified=True)


@pytest.fixture(scope="session")
def sealed_groups() -> dict[str, str]:
    """Source-to-city labels from the sealed endpoint table (ledgers carry none)."""
    return read_groups(artefact("cohort_tables"))
