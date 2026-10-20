"""The study price sweep and its published tables.

The cohort is re-priced with :func:`qrq.sweep.sweep` at 45 points: coherent
lookup prices {100, 30, 10, 3, 1} x coherent geometry prices {10000, 3000,
1000, 300, 100, 30, 10, 3, 1}; classical geometry, gate price and repetitions
stay at 1. Forward pairs are compared with those at ``L1`` (retained, added,
lost). Three window subsets are reported next to the pooled readouts:

* ``15min``: windows of 900 s;
* ``width_le_1km``: windows at most 1000 m wide;
* ``K_ge_20000``: windows with at least 20000 answers.

:func:`price_tables` returns the grid, per-source and per-source-and-axis
tables with the column names of the sealed tables, where the group label is
the source's city.
"""
from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from qrq.prices import L1, PriceTable
from qrq.sweep import Row, SweepCohort, SweepTables, cohort_from_ledger, price_grid, sweep

LOOKUP_PRICES: tuple[int, ...] = (100, 30, 10, 3, 1)
GEOMETRY_PRICES: tuple[int, ...] = (10000, 3000, 1000, 300, 100, 30, 10, 3, 1)
REPORT_POINTS: tuple[tuple[int, int], ...] = ((100, 10000), (10, 1000), (1, 100), (1, 1))
"""``(lookup, g_quantum)`` points reported in the text."""

FINE_DURATION_S = 900
FINE_WIDTH_M = 1000
LARGE_ANSWER = 20000

REPORTED: dict[tuple[int, int], tuple[int, float, int, int]] = {
    (100, 10000): (742, 33.13, 1060, 11),
    (10, 1000): (1253, 19.29, 1348, 28),
    (1, 100): (1514, 16.89, 1368, 46),
    (1, 1): (1559, 16.60, 1357, 49),
}
"""Published (lower windows, median Q/C at two decimals, forward, reverse) per report point."""

PUBLISHED_COLUMNS = {"group": "city", "groups_with_forward": "cities_with_forward"}
"""qrq row keys renamed to the column names of the sealed tables."""


def study_price_grid() -> list[PriceTable]:
    """The 45 price points, lookup price outer, ``L1`` first."""
    return price_grid(LOOKUP_PRICES, GEOMETRY_PRICES, base=L1)


def study_subsets(cohort: SweepCohort) -> list[tuple[str, np.ndarray]]:
    """The three reported window subsets of ``cohort``."""
    return [
        ("15min", cohort.duration_s == FINE_DURATION_S),
        ("width_le_1km", cohort.width_m <= FINE_WIDTH_M),
        ("K_ge_20000", cohort.k >= LARGE_ANSWER),
    ]


def _published(row: Row) -> Row:
    return {PUBLISHED_COLUMNS.get(name, name): value for name, value in row.items()}


def price_tables(ledger_cohort: Any, groups: Mapping[str, str] | None = None) -> SweepTables:
    """The three published sweep tables of an audited cohort.

    ``ledger_cohort`` is a :class:`qrq.ledger.LedgerCohort` audited at ``L1``
    (:func:`scale_reversal.cohort.reproduce`); ``groups`` maps each source to
    its city (:func:`scale_reversal.archive.read_groups`).
    """
    cohort = cohort_from_ledger(ledger_cohort, group_of=groups)
    tables = sweep(cohort, study_price_grid(), subsets=study_subsets(cohort), reference=L1)
    return SweepTables(
        grid=[_published(r) for r in tables.grid],
        by_source=[_published(r) for r in tables.by_source],
        pairs=[_published(r) for r in tables.pairs],
    )
