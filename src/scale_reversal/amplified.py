"""The amplitude-amplification sensitivity of the published cohort.

The sensitivity re-envelopes the cohort with unknown-K amplitude
amplification admitted on the originally selected quantum tree
(:func:`qrq.engine.include_amplified`, via
``scale_reversal.cohort.reproduce(..., amplified=True)``):
``Q = min(Q_FW, Q_AA)``, the classical side unchanged, the tree choice not
re-optimised. It is compared pair by pair with the first-witness cohort:

* ``retained``: first-witness forward pairs that stay forward;
* ``both_quantum_lower``: first-witness forward pairs whose two windows both
  become quantum-favourable;
* ``amplified_only``: directions when the AA cost replaces the first-witness
  cost outright, ``D = log2(Q_AA / C)``.
"""
from __future__ import annotations

import collections
import math
from typing import Any, Mapping

from qrq.ledger import LedgerCohort, PairRecord
from qrq.workload import classify_pair

from .price_sweep import FINE_DURATION_S, FINE_WIDTH_M

PUBLISHED_AA = dict(
    windows=13370, quantum_lower=869, pairs=17592, forward=1211, reverse=13,
    legacy_forward=1060, retained=973, both_quantum_lower=87,
    fine_duration_lower=0, fine_width_lower=3, amplified_cheaper=11685,
    amplified_only_forward=1200, amplified_only_reverse=11, sources_with_forward=12,
)
"""Published sensitivity counts (pooled over the cohort)."""

PUBLISHED_AA_GROUPS = (11, 13)
"""Groups (cities) with an AA-inclusive forward pair, and all groups."""

BY_SOURCE_COLUMNS = (
    "comparator", "source_id", "pairs", "source_days",
    "legacy_forward", "legacy_reverse", "legacy_no_cross",
    "aa_only_forward", "aa_only_reverse", "aa_only_no_cross",
    "joint_forward", "joint_reverse", "joint_no_cross",
    "legacy_forward_retained", "legacy_forward_both_now_Q_lower",
)
"""Columns of the sealed per-source table."""

PairKey = tuple[str, str, str, str, str]


def pair_key(pair: PairRecord) -> PairKey:
    """``(source_id, date, axis, small_query, large_query)``."""
    return (pair.source_id, pair.date, pair.axis, pair.small_query, pair.large_query)


def amplified_only_directions(joint: LedgerCohort) -> dict[PairKey, str]:
    """Pair directions when the AA cost replaces the first-witness cost outright."""
    d = {(w.source_id, w.date, w.query_id): math.log2(w.amplified_cost / w.C) for w in joint.windows}
    return {pair_key(p): classify_pair(d[(p.source_id, p.date, p.small_query)],
                                       d[(p.source_id, p.date, p.large_query)])
            for p in joint.pairs}


def sensitivity(legacy: LedgerCohort, joint: LedgerCohort, groups: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Pooled sensitivity counts (the keys of :data:`PUBLISHED_AA`).

    ``legacy`` and ``joint`` are the first-witness and AA-inclusive cohorts of
    the same ledgers. With ``groups`` the result also holds
    ``groups_with_forward`` and ``groups``.
    """
    old = {pair_key(p): p.direction for p in legacy.pairs}
    new = {pair_key(p): p for p in joint.pairs}
    if old.keys() != new.keys():
        raise ValueError("the two cohorts must hold the same pairs")
    was_forward = [k for k, d in old.items() if d == "forward"]
    alone = collections.Counter(amplified_only_directions(joint).values())
    directions = joint.direction_counts()
    forward_sources = {p.source_id for p in joint.pairs if p.direction == "forward"}
    out: dict[str, Any] = dict(
        windows=joint.window_count,
        quantum_lower=joint.quantum_lower_count,
        pairs=len(joint.pairs),
        forward=int(directions["forward"]),
        reverse=int(directions["reverse"]),
        legacy_forward=len(was_forward),
        retained=sum(new[k].direction == "forward" for k in was_forward),
        both_quantum_lower=sum(new[k].small_D < 0 and new[k].large_D < 0 for k in was_forward),
        fine_duration_lower=sum(w.quantum_lower for w in joint.windows if w.duration_s == FINE_DURATION_S),
        fine_width_lower=sum(w.quantum_lower for w in joint.windows if w.width_m <= FINE_WIDTH_M),
        amplified_cheaper=sum(w.amplified_cost < w.filter_cost for w in joint.windows),
        amplified_only_forward=int(alone["forward"]),
        amplified_only_reverse=int(alone["reverse"]),
        sources_with_forward=len(forward_sources),
    )
    if groups is not None:
        out["groups_with_forward"] = len({groups[s] for s in forward_sources})
        out["groups"] = len(set(groups.values()))
    return out


def aa_by_source(legacy: LedgerCohort, joint: LedgerCohort) -> list[dict[str, Any]]:
    """Per-source pair directions in the layout of the sealed table (comparator ``envelope``)."""
    old = {pair_key(p): p.direction for p in legacy.pairs}
    alone = amplified_only_directions(joint)
    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    dates: dict[str, set[str]] = collections.defaultdict(set)
    for p in joint.pairs:
        key = pair_key(p)
        c = counts[p.source_id]
        dates[p.source_id].add(p.date)
        c["pairs"] += 1
        c[f"legacy_{old[key]}"] += 1
        c[f"aa_only_{alone[key]}"] += 1
        c[f"joint_{p.direction}"] += 1
        c["legacy_forward_retained"] += old[key] == "forward" and p.direction == "forward"
        c["legacy_forward_both_now_Q_lower"] += old[key] == "forward" and p.small_D < 0 and p.large_D < 0
    rows = []
    for source in sorted(counts):
        row: dict[str, Any] = {"comparator": "envelope", "source_id": source}
        for name in BY_SOURCE_COLUMNS[2:]:
            row[name] = len(dates[source]) if name == "source_days" else int(counts[source][name])
        rows.append(row)
    return rows
