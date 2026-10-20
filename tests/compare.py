"""Locate sealed artefacts for the tests and compare tables."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Collection, Mapping, Sequence

import pytest

from scale_reversal.archive import read_csv
from scale_reversal.evidence import EvidenceNotConfigured, locate

__all__ = ["artefact", "assert_rows_equal", "read_csv"]


def artefact(name: str) -> Path:
    """Directory of a sealed artefact, or skip the calling test when not configured."""
    try:
        return locate(name)
    except EvidenceNotConfigured as error:
        pytest.skip(str(error))
    except NotADirectoryError as error:
        pytest.fail(str(error))


def _matches(stored: str, value: Any, rel_tol: float) -> bool:
    if stored == "":
        return value is None or (isinstance(value, float) and math.isnan(value))
    if isinstance(value, (bool, str)):
        return stored == str(value)
    if isinstance(value, int):
        return int(stored) == value
    if rel_tol:
        return math.isclose(float(stored), float(value), rel_tol=rel_tol, abs_tol=rel_tol)
    return float(stored) == float(value)


def assert_rows_equal(
    stored: Sequence[Mapping[str, str]],
    ours: Sequence[Mapping[str, Any]],
    tolerances: Mapping[str, float] | None = None,
    ignore: Collection[str] = (),
) -> None:
    """Compare recomputed rows with a sealed CSV table, column by column.

    Columns and row order must agree. Numbers compare exactly (CSV floats are
    stored at full precision) unless ``tolerances`` gives a relative
    tolerance for a column; an empty cell matches ``None`` or ``nan``.
    """
    tolerances = tolerances or {}
    assert len(stored) == len(ours)
    for i, (a, b) in enumerate(zip(stored, ours)):
        assert [c for c in a if c not in ignore] == [c for c in b if c not in ignore], i
        for column, text in a.items():
            if column in ignore:
                continue
            assert _matches(text, b[column], tolerances.get(column, 0.0)), (i, column, text, b[column])
