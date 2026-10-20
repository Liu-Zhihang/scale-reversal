"""The reconstruction-task comparison against the sealed tables (skipped unless configured).

Needs the task archive: the sealed archive root holding the comparison run
and the input runs listed in its ``inputs/freeze.json``.
"""
from __future__ import annotations

import pytest

from scale_reversal import tasks
from scale_reversal.cli import family_readouts
from scale_reversal.task_inputs import FAMILY_ORDER, PUBLISHED_FAMILIES, RESULTS, load_task_inputs

from compare import artefact, assert_rows_equal, read_csv


@pytest.fixture(scope="module")
def sealed_tasks():
    pytest.importorskip("pandas")
    root = artefact("task_archive")
    pairs, registry = load_task_inputs(root)
    return root, pairs, tasks.compare_crossings(pairs, registry, FAMILY_ORDER)


def test_task_tables_match_sealed(sealed_tasks):
    """Family, source, stratum and category tables are reproduced exactly."""
    root, pairs, result = sealed_tasks
    tables = root / RESULTS
    assert_rows_equal(read_csv(tables / "family_summary.csv"), result.family_rows())
    assert_rows_equal(read_csv(tables / "by_task_source.csv"), result.source_rows())
    assert_rows_equal(read_csv(tables / "strata.csv"), result.stratum_rows())
    assert_rows_equal(read_csv(tables / "category_summary.csv"), tasks.category_summary(pairs))


def test_published_family_readouts(sealed_tasks):
    root, pairs, result = sealed_tasks
    speed, monitoring = (f.row() for f in result.families)
    assert family_readouts(speed) == PUBLISHED_FAMILIES["speed"]
    assert family_readouts(monitoring) == PUBLISHED_FAMILIES["monitoring"]
    assert (speed["operational_label"], monitoring["operational_label"]) == (
        tasks.NO_INFORMATION, tasks.CROSSING_WORSE)
    counts = {family: sum(p.family == family for p in pairs) for family in FAMILY_ORDER}
    assert counts == {"speed": 15432, "monitoring": 3552}
    assert sum(p.supported for p in pairs if p.family == "speed") == 12912
