"""The published cohort against the sealed evidence (skipped unless configured).

Needs the ledgers; the table checks need the cohort tables and the window
check the cohort inputs (``SR_EVIDENCE`` or the artefact variables, see
docs/reproduction.md).
"""
from __future__ import annotations

import collections
import math

import pytest

from qrq.workload import classify_pair

from scale_reversal.archive import read_reference_points, read_registered_queries
from scale_reversal.cohort import PUBLISHED, PUBLISHED_BY_SOURCE
from scale_reversal.grid import study_windows

from compare import artefact


def test_ledger_costs_and_envelope(sealed_reproduction):
    """Every stored L1 route cost is recomputed from its resource vectors."""
    r = sealed_reproduction
    assert r.days == PUBLISHED["days"] and r.ledgers == PUBLISHED["ledgers"]
    assert r.priced_routes > 0 and r.priced_routes % 5 == 0
    assert r.max_relative_error <= 1e-12
    summary = r.summary()
    for key in ("windows", "quantum_lower", "pairs", "forward", "reverse"):
        assert summary[key] == PUBLISHED[key], key
    for source, (windows, lower, forward, reverse) in PUBLISHED_BY_SOURCE.items():
        got = summary["by_source"][source]
        assert (got["windows"], got["quantum_lower"], got["forward"], got["reverse"]) == (
            windows, lower, forward, reverse), source
    for w in r.windows:
        assert w.D == math.log2(w.Q / w.C)
        assert math.isclose(w.Q, w.prefix + w.trials * w.trial_cost, rel_tol=1e-12)


def _tables():
    pd = pytest.importorskip("pandas")
    root = artefact("cohort_tables")
    keep = dict(dtype={"date": str, "anchor": str, "query_id": str, "small_query": str, "large_query": str})
    ep = pd.read_csv(root / "endpoints.csv.gz", **keep)
    sp = pd.read_csv(root / "scale_pairs.csv.gz", **keep)
    select = lambda df: df[(df.comparator == "envelope") & (df.arm == "baseline") & (df.variant == "base")]
    return select(ep), select(sp)


def test_published_counts_in_tables():
    """The sealed tables state the published counts; directions re-classify."""
    ep, sp = _tables()
    assert len(ep) == PUBLISHED["windows"]
    assert int((ep.Q < ep.C).sum()) == PUBLISHED["quantum_lower"]
    assert len(sp) == PUBLISHED["pairs"]
    directions = [classify_pair(a, b) for a, b in zip(sp.small_D, sp.large_D)]
    assert directions == sp.direction.tolist()
    counts = collections.Counter(directions)
    assert (counts["forward"], counts["reverse"]) == (PUBLISHED["forward"], PUBLISHED["reverse"])


def test_envelope_matches_tables(sealed_reproduction):
    """Recomputed envelopes and pairs equal the sealed tables row by row."""
    ep, sp = _tables()
    table = {(r.source_id, r.date, r.query_id): r for r in ep.itertuples(index=False)}
    assert len(table) == len(ep)
    ours = {(w.source_id, w.date, w.query_id): w for w in sealed_reproduction.windows}
    assert ours.keys() == table.keys()
    for key, w in ours.items():
        t = table[key]
        assert (w.k, w.n, w.M, w.G) == (t.k, t.n, t.M, t.G)
        assert (w.quantum_tree, w.classical_tree, w.classical_route) == (t.q_tree, t.c_tree, t.c_route)
        for name in ("Q", "C", "D", "trials", "prefix", "trial_cost"):
            assert math.isclose(getattr(w, name), getattr(t, name), rel_tol=1e-12, abs_tol=1e-12), (key, name)
        assert w.quantum_lower == bool(t.lower)
    table_pairs = {(r.source_id, r.date, r.axis, r.small_query, r.large_query): r.direction
                   for r in sp.itertuples(index=False)}
    our_pairs = {(p.source_id, p.date, p.axis, p.small_query, p.large_query): p.direction
                 for p in sealed_reproduction.pairs}
    assert our_pairs == table_pairs


def test_registered_windows_match_sealed_inputs():
    """The study grid reproduces every sealed baseline window exactly."""
    root = artefact("cohort_inputs")
    references = read_reference_points(root)
    assert len(references) == 14
    for source, (x, y) in references.items():
        baseline = [q for q in read_registered_queries(root, source) if q.get("arm") == "baseline"]
        windows = study_windows(x, y)
        assert len(baseline) == len(windows) == 648
        for q, w in zip(baseline, windows):
            assert q["query_id"] == w.query_id
            assert q["bounds"] == list(w.box.bounds)
            assert tuple(q["anchor_index"]) == w.anchor_index
            assert q["status"] == w.status
