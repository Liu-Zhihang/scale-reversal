"""The published price sweep against the sealed evidence (skipped unless configured).

Needs the ledgers; the full table comparison also needs the cohort tables
(city labels) and the sweep tables.
"""
from __future__ import annotations

import numpy as np
import pytest

import qrq
from qrq import sweep

from scale_reversal.price_sweep import REPORTED, price_tables

from compare import artefact, assert_rows_equal, read_csv


@pytest.fixture(scope="module")
def sealed_cohort(sealed_reproduction):
    return sweep.cohort_from_ledger(sealed_reproduction)


def test_closed_form_reproduces_l1_ledgers(sealed_reproduction, sealed_cohort):
    """At L1 the closed form equals the ledger costs and the published directions."""
    point = sweep.reprice(sealed_cohort, qrq.L1)
    ledger_q = np.array([[t.Q for t in w.trees] for w in sealed_reproduction.windows])
    ledger_c = np.array([[t.C for t in w.trees] for w in sealed_reproduction.windows])
    assert np.max(np.abs(point.Q_tree - ledger_q) / ledger_q) < 1e-12
    np.testing.assert_array_equal(point.C_tree, ledger_c)
    envelope = np.array([w.Q for w in sealed_reproduction.windows])
    assert np.max(np.abs(point.Q - envelope) / envelope) < 1e-12
    np.testing.assert_array_equal(point.C, [w.C for w in sealed_reproduction.windows])
    assert point.forward.tolist() == [p.direction == "forward" for p in sealed_reproduction.pairs]
    assert point.reverse.tolist() == [p.direction == "reverse" for p in sealed_reproduction.pairs]


def test_reported_price_points(sealed_reproduction):
    tables = price_tables(sealed_reproduction)
    rows = {(r["lookup"], r["quantum_geometry"]): r for r in tables.grid}
    assert len(rows) == 45
    for point, (lower, median, forward, reverse) in REPORTED.items():
        r = rows[point]
        assert (r["eligible_windows"], r["eligible_pairs"]) == (13370, 17592)
        assert (r["lower_windows"], round(r["q_over_c_median"], 2), r["forward_pairs"], r["reverse_pairs"]) == (
            lower, median, forward, reverse), point
    unit = rows[(1, 1)]
    assert (unit["forward_retained"], unit["forward_added"], unit["forward_lost"]) == (907, 450, 153)
    assert (unit["15min_lower"], unit["15min_windows"], unit["width_le_1km_lower"], unit["width_le_1km_windows"]) == (
        49, 2917, 47, 5429)
    l1 = rows[(100, 10000)]
    assert (l1["forward_retained"], l1["forward_added"], l1["forward_lost"]) == (1060, 0, 0)
    assert (l1["15min_lower"], l1["width_le_1km_lower"]) == (0, 2)
    forward = [r["forward_pairs"] for r in tables.grid]
    assert (min(forward), max(forward)) == (1060, 1377)


def test_price_tables_match_sealed_sweep(sealed_reproduction, sealed_groups):
    """All three sealed sweep tables are reproduced bit for bit."""
    root = artefact("sweep_tables")
    tables = price_tables(sealed_reproduction, sealed_groups)
    assert_rows_equal(read_csv(root / "price_grid.csv"), tables.grid)
    assert_rows_equal(read_csv(root / "price_by_source.csv"), tables.by_source)
    assert_rows_equal(read_csv(root / "price_pairs.csv"), tables.pairs)
    l1 = tables.grid[0]
    assert (l1["sources_with_forward"], l1["cities_with_forward"]) == (12, 11)
    assert l1["q_over_c_median"] == 33.134379608128285
