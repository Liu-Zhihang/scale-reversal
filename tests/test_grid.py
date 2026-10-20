"""The registered study grid."""
from __future__ import annotations

import itertools

import pytest

from qrq.workload import adjacent_pairs

from scale_reversal.grid import STUDY_GRID, study_windows

WIDTHS = (250, 500, 1000, 2000, 5000, 10000)
DURATIONS = (900, 3600, 21600, 86400)
CENTRES = (21600, 43200, 64800)


def test_grid_constants():
    assert (STUDY_GRID.widths, STUDY_GRID.durations, STUDY_GRID.centres) == (WIDTHS, DURATIONS, CENTRES)
    assert (STUDY_GRID.anchors, STUDY_GRID.anchor_step, STUDY_GRID.day_seconds) == (3, 20000 / 3, 86400)
    assert STUDY_GRID.size == 648


@pytest.mark.parametrize("cx,cy", [(0.0, 0.0), (448478.20497292466, 4417664.577536389), (-1234.5, 98765.25)])
def test_study_windows_formulas(cx, cy):
    windows = study_windows(cx, cy)
    assert len(windows) == 648 and len({w.query_id for w in windows}) == 648
    expected = itertools.product(range(3), range(3), CENTRES, WIDTHS, DURATIONS)
    for w, (ix, iy, tc, width, d) in zip(windows, expected):
        x = cx + (ix - 1) * 20000 / 3
        y = cy + (iy - 1) * 20000 / 3
        assert w.query_id == f"g{ix}{iy}_c{tc}_w{width}_d{d}"
        assert list(w.box.bounds) == [x - width / 2, x + width / 2, y - width / 2, y + width / 2,
                                      tc - d / 2, tc + d / 2]
        unsupported = tc - d / 2 < 0 or tc + d / 2 > 86400
        assert w.status == ("unsupported_index_span" if unsupported else "scheduled")
    assert sum(not w.supported for w in windows) == 108


def test_study_pairs():
    pairs = adjacent_pairs(study_windows(0.0, 0.0), STUDY_GRID)
    assert len(pairs) == 9 * 3 * ((6 - 1) * 4 + 6 * (4 - 1)) == 1026
