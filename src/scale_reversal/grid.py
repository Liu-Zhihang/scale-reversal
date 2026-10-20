"""The registered window grid of the study.

Each source-day is queried with the same grid around its reference point
``(cx, cy)`` (read from the sealed inputs):

* a 3 x 3 anchor lattice with spacing 20000/3 m;
* temporal centres 21600, 43200 and 64800 s (06:00, 12:00, 18:00);
* square widths 250, 500, 1000, 2000, 5000 and 10000 m;
* durations 900, 3600, 21600 and 86400 s.

That is 648 windows per source-day, 108 of which leave the index day and are
registered as ``unsupported_index_span``. Registration and pairing are
:func:`qrq.register_windows` and :func:`qrq.adjacent_pairs`.
"""
from __future__ import annotations

from qrq.workload import Window, WindowGrid, register_windows

STUDY_GRID = WindowGrid(
    widths=(250, 500, 1000, 2000, 5000, 10000),
    durations=(900, 3600, 21600, 86400),
    centres=(21600, 43200, 64800),
    anchor_step=20000 / 3,
    anchors=3,
)


def study_windows(cx: float, cy: float) -> list[Window]:
    """The 648 registered windows of one source-day around ``(cx, cy)``."""
    return register_windows(cx, cy, STUDY_GRID)
