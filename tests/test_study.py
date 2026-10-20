"""Cohort reproduction, price sweep and AA sensitivity on the synthetic archive."""
from __future__ import annotations

import dataclasses

import pytest

import qrq
from qrq.ledger import audit_cohort

from scale_reversal import amplified, archive, cohort, price_sweep
from scale_reversal.grid import STUDY_GRID

from synthetic_archive import ANCHORS, DAYS, GROUPS

GRID_COLUMNS = (
    "lookup,quantum_geometry,eligible_windows,lower_windows,q_over_c_median,15min_windows,15min_lower,"
    "15min_ratio_median,width_le_1km_windows,width_le_1km_lower,width_le_1km_ratio_median,K_ge_20000_windows,"
    "K_ge_20000_lower,K_ge_20000_ratio_median,structure_share_q25,structure_share_median,structure_share_q75,"
    "prefix_share_q25,prefix_share_median,prefix_share_q75,M_over_K_q25,M_over_K_median,M_over_K_q75,"
    "G_over_K_q25,G_over_K_median,G_over_K_q75,C_over_K_q25,C_over_K_median,C_over_K_q75,forward_pairs,"
    "reverse_pairs,eligible_pairs,sources_with_forward,cities_with_forward,forward_retained,forward_added,"
    "forward_lost,q_tree_tie_windows,c_tree_tie_windows"
).split(",")
"""Column order of the sealed price grid table."""

STUDY_GRID_WINDOWS = qrq.register_windows(0.0, 0.0, STUDY_GRID)


def test_published_constants_are_consistent():
    rows = cohort.PUBLISHED_BY_SOURCE.values()
    assert len(cohort.PUBLISHED_BY_SOURCE) == 14
    assert tuple(map(sum, zip(*rows))) == tuple(cohort.PUBLISHED[k] for k in ("windows", "quantum_lower",
                                                                               "forward", "reverse"))


def test_reproduce_is_the_generic_audit(synthetic_archive, synthetic_cohorts):
    legacy, _ = synthetic_cohorts
    days = archive.find_ledger_days(synthetic_archive / "ledgers")
    generic = audit_cohort(days, STUDY_GRID, arms=("baseline", "perturb"), arm="baseline", variant="base")
    assert [w.query_id for w in legacy.windows] == [w.query_id for w in generic.windows]
    assert legacy.pairs == generic.pairs and legacy.pairs
    windows_per_day = sum(w.anchor_index in ANCHORS for w in STUDY_GRID_WINDOWS)
    assert (legacy.days, legacy.ledgers, legacy.rows) == (len(DAYS), 3 * len(DAYS),
                                                          3 * len(DAYS) * (windows_per_day + 1))
    assert legacy.exact_cost_matches == legacy.priced_routes and "sentinel" not in {w.query_id for w in legacy.windows}



def test_study_price_grid():
    grid = price_sweep.study_price_grid()
    assert len(grid) == 45 and grid[0] == qrq.L1
    assert [p.lookup for p in grid[::9]] == list(price_sweep.LOOKUP_PRICES)
    assert set(price_sweep.REPORT_POINTS) <= {(p.lookup, p.g_quantum) for p in grid}
    assert set(price_sweep.REPORTED) == set(price_sweep.REPORT_POINTS)


def test_price_tables_layout(synthetic_cohorts):
    legacy, _ = synthetic_cohorts
    tables = price_sweep.price_tables(legacy, GROUPS)
    assert len(tables.grid) == 45 and list(tables.grid[0]) == GRID_COLUMNS
    l1 = tables.grid[0]
    assert (l1["forward_retained"], l1["forward_added"], l1["forward_lost"]) == (l1["forward_pairs"], 0, 0)
    assert l1["lower_windows"] == legacy.quantum_lower_count
    assert {row["city"] for row in tables.by_source} == {"north"}
    assert list(tables.by_source[0])[-3:] == ["source_id", "city", "source_days"]
    assert all(row["cities_with_forward"] <= 1 for row in tables.grid)
    assert list(tables.pairs[0]) == ["lookup", "quantum_geometry", "source_id", "axis", "eligible_pairs",
                                     "forward_pairs", "reverse_pairs", "no_cross_pairs", "forward_retained",
                                     "forward_added", "forward_lost"]
    assert any(row["forward_pairs"] for row in tables.grid)


def test_amplified_sensitivity(synthetic_cohorts):
    legacy, joint = synthetic_cohorts
    s = amplified.sensitivity(legacy, joint, GROUPS)
    assert set(amplified.PUBLISHED_AA) <= set(s) and (s["groups"], s["groups_with_forward"] <= 1) == (1, True)
    assert s["windows"] == legacy.window_count and s["pairs"] == len(legacy.pairs)
    assert s["retained"] + s["both_quantum_lower"] <= s["legacy_forward"]
    assert s["amplified_cheaper"] == sum(w.quantum_route == "QRQ_AA" for w in joint.windows) > 0
    rows = amplified.aa_by_source(legacy, joint)
    assert [tuple(r) for r in rows] == [amplified.BY_SOURCE_COLUMNS] * len(rows)
    assert [r["source_id"] for r in rows] == sorted({s for s, _, _ in DAYS})
    assert sum(r["pairs"] for r in rows) == s["pairs"]
    assert sum(r["joint_forward"] for r in rows) == s["forward"]
    assert sum(r["aa_only_forward"] for r in rows) == s["amplified_only_forward"]
    assert sum(r["legacy_forward_retained"] for r in rows) == s["retained"]
    with pytest.raises(ValueError):
        amplified.sensitivity(legacy, dataclasses.replace(joint, pairs=joint.pairs[1:]))
