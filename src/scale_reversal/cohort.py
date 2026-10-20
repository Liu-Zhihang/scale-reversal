"""Reproduction of the published access cohort from the sealed ledgers.

The cohort is every non-empty, fully supported baseline window (arm
``baseline``, variant ``base``) of the 107 registered source-days, with its
envelope recomputed from the per-tree ledgers by :func:`qrq.ledger.audit_cohort`
under the ``L1`` prices, and the adjacent-scale pairs of
:data:`scale_reversal.grid.STUDY_GRID` within each source-day. Envelopes are
built for the ``baseline`` and ``perturb`` arms, as in the sealed analysis;
only the baseline arm enters the cohort.
"""
from __future__ import annotations

from pathlib import Path

from qrq.ledger import LedgerCohort, audit_cohort
from qrq.prices import L1, PriceTable

from .archive import find_ledger_days
from .grid import STUDY_GRID

ENDPOINT_ARMS = ("baseline", "perturb")
COHORT_ARM = "baseline"
COHORT_VARIANT = "base"

PUBLISHED = dict(days=107, ledgers=321, windows=13370, quantum_lower=742, pairs=17592, forward=1060, reverse=11)
"""Published cohort totals."""

PUBLISHED_BY_SOURCE: dict[str, tuple[int, int, int, int]] = {
    "tdrive": (3305, 208, 330, 0),
    "geolife": (265, 4, 8, 0),
    "jinan": (2460, 232, 345, 0),
    "dublin": (282, 30, 41, 9),
    "porto": (240, 2, 4, 0),
    "montreal": (1253, 18, 32, 0),
    "barcelona": (85, 0, 0, 0),
    "rio": (817, 27, 47, 0),
    "stellenbosch": (159, 7, 10, 0),
    "nyc_mat": (328, 28, 34, 0),
    "paris_mat": (138, 0, 0, 0),
    "sf_cabspotting": (1698, 93, 101, 0),
    "rome_taxi": (2150, 91, 104, 0),
    "brighton_shl": (190, 2, 4, 2),
}
"""Published per-source table: non-empty windows, ``Q < C`` windows, forward and reverse pairs."""


def reproduce(
    ledgers: str | Path, prices: PriceTable = L1, amplified: bool = False, rel_tol: float = 1e-12
) -> LedgerCohort:
    """Re-price all sealed ledgers and rebuild the cohort envelopes and pairs.

    ``amplified=True`` admits amplitude amplification on the selected quantum
    tree (the published sensitivity analysis).
    """
    return audit_cohort(
        find_ledger_days(ledgers), STUDY_GRID, prices, rel_tol, amplified,
        arms=ENDPOINT_ARMS, arm=COHORT_ARM, variant=COHORT_VARIANT,
    )
