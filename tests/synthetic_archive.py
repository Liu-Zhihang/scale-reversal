"""A small synthetic evidence archive in the sealed layout.

Ledgers are written with :func:`qrq.ledger.ledger_row` for the study grid at
two anchors of three synthetic source-days, under
``<root>/<host>/outputs/<source>/<date>/<tree>.jsonl.gz``; a minimal
``endpoints.csv.gz`` carries the group label of each source.
"""
from __future__ import annotations

import csv
import gzip
from pathlib import Path
from typing import Sequence

import numpy as np

import qrq
from qrq.ledger import ledger_row, write_ledger

from scale_reversal.archive import GROUP_COLUMN
from scale_reversal.grid import STUDY_GRID, study_windows

CENTRE = (20000.0, 20000.0)
ANCHORS = ((1, 1), (0, 2))
DAYS = (("alpha", "2020-01-01", 11), ("alpha", "2020-01-02", 12), ("beta", "2020-01-01", 13))
GROUPS = {"alpha": "north", "beta": "north"}


def cloud(n: int, seed: int) -> np.ndarray:
    """Hub-and-spoke cloud around :data:`CENTRE` covering the used anchors."""
    rng = np.random.default_rng(seed)
    cx, cy = CENTRE
    step = STUDY_GRID.anchor_step
    hubs = np.array([[cx, cy], [cx - step, cy + step], [cx + 0.4 * step, cy - 0.3 * step]])
    which = rng.integers(0, len(hubs), n)
    spread = rng.choice([150.0, 600.0, 2500.0], n)
    x = hubs[which, 0] + rng.normal(0, 1, n) * spread
    y = hubs[which, 1] + rng.normal(0, 1, n) * spread
    t = rng.uniform(0, 86400, n)
    return qrq.make_points(x, y, t, rng.integers(0, 40, n).astype(np.int64))


def write_archive(root: Path, days: Sequence[tuple[str, str, int]] = DAYS, n: int = 2500) -> Path:
    """Write the synthetic archive under ``root`` and return ``root``.

    Baseline windows carry arm ``baseline`` and variant ``base``; a copy of
    each window with arm ``sentinel`` and no window metadata checks that
    such rows are priced but never enveloped.
    """
    ledgers = root / "ledgers"
    for source, date, seed in days:
        points = cloud(n, seed)
        windows = [w for w in study_windows(*CENTRE) if w.anchor_index in ANCHORS]
        for kind in qrq.TREE_KINDS:
            index = qrq.SpatioTemporalIndex.build(points, kind=kind)
            rows = [ledger_row(w, index, source_id=source, date=date, arm="baseline", variant="base")
                    for w in windows]
            sentinel = ledger_row(windows[0], index, source_id=source, date=date, arm="sentinel")
            for name in ("anchor_index", "width_m", "duration_s", "temporal_center_s"):
                del sentinel[name]
            sentinel["query_id"] = "sentinel"
            write_ledger(ledgers / "host" / "outputs" / source / date / f"{kind}.jsonl.gz", rows + [sentinel])
    tables = root / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    with gzip.open(tables / "endpoints.csv.gz", "wt", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_id", GROUP_COLUMN, "query_id"])
        writer.writeheader()
        for source, group in GROUPS.items():
            writer.writerow({"source_id": source, GROUP_COLUMN: group, "query_id": "q"})
    return root
