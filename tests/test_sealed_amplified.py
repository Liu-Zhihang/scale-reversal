"""The AA sensitivity against the sealed evidence (skipped unless configured).

Needs the ledgers; the city count also needs the cohort tables and the
row-level comparison the AA tables.
"""
from __future__ import annotations

import math

from scale_reversal.amplified import PUBLISHED_AA, PUBLISHED_AA_GROUPS, aa_by_source, sensitivity

from compare import artefact, assert_rows_equal, read_csv


def test_amplified_counts(sealed_reproduction, sealed_amplified):
    s = sensitivity(sealed_reproduction, sealed_amplified)
    assert {k: s[k] for k in PUBLISHED_AA} == PUBLISHED_AA
    assert sum(w.quantum_route == "QRQ_AA" for w in sealed_amplified.windows) == PUBLISHED_AA["amplified_cheaper"]
    for a, b in zip(sealed_reproduction.windows, sealed_amplified.windows):
        assert (a.quantum_tree, a.C, a.Q) == (b.quantum_tree, b.C, b.filter_cost)


def test_amplified_cities(sealed_reproduction, sealed_amplified, sealed_groups):
    s = sensitivity(sealed_reproduction, sealed_amplified, sealed_groups)
    assert (s["groups_with_forward"], s["groups"]) == PUBLISHED_AA_GROUPS


def test_amplified_matches_sealed_tables(sealed_reproduction, sealed_amplified):
    """Per-window AA costs and the per-source table equal the sealed AA tables.

    ``Q_aa`` and its inputs are bit-identical. The sealed ``Q_joint`` and
    ``D_joint`` were computed from first-witness costs parsed with a
    non-round-trip CSV reader, which shifts some values by one unit in the
    last place; they therefore compare within ``4e-16`` relative error. No
    sign, direction or count is affected.
    """
    root = artefact("aa_tables")
    ours = {(w.source_id, w.date, w.query_id): w for w in sealed_amplified.windows}
    rows = [r for r in read_csv(root / "aa_endpoints.csv.gz") if r["comparator"] == "envelope"]
    assert len(rows) == len(ours) == PUBLISHED_AA["windows"]
    for r in rows:
        w = ours[(r["source_id"], r["date"], r["query_id"])]
        tree = next(t for t in w.trees if t.tree == w.quantum_tree)
        assert (r["q_tree"], int(r["M"]), int(r["G"]), int(r["address_bits"])) == (
            w.quantum_tree, tree.M, tree.G, tree.bits)
        assert (float(r["P0"]), float(r["Q_aa"]), float(r["C"])) == (tree.P0, w.amplified_cost, w.C)
        assert math.isclose(float(r["Q_joint"]), w.Q, rel_tol=4e-16)
        assert math.isclose(float(r["D_joint"]), w.D, rel_tol=4e-16, abs_tol=1e-15)
        assert (float(r["D_joint"]) < 0) == w.quantum_lower
    stored = [r for r in read_csv(root / "aa_by_source.csv") if r["comparator"] == "envelope"]
    assert_rows_equal(stored, aa_by_source(sealed_reproduction, sealed_amplified))
