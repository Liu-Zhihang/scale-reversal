"""Shared inputs for the Figure 1 parts.

All parts use one 6 km Rome tile centred on the densest taxi trajectories
(SR_FIGURE_DATA/basemap/rome_osm.json, rome_traces.json; see fetch_rome_layers.py),
one cube time window and one query anchor, so the parts agree when assembled.
Trace coordinates are metres from the tile centre and seconds of the day.
Parts are written to SR_FIGURE_OUT/figure1_parts.
"""
from functools import lru_cache
import json
from pathlib import Path
import shutil
import tempfile
import time

import matplotlib.pyplot as plt
import numpy as np

import paths as P
import style as S

OUT = P.figure1_parts()
OUT.mkdir(parents=True, exist_ok=True)
HALF = 3000.0
CUBE_WINDOW_S = (7 * 3600 + 40 * 60, 8 * 3600 + 20 * 60)      # 07:40-08:20 rises through the cube
TEALS = [S.CLASSICAL_DEEP, S.CLASSICAL, S.CLASSICAL_MID, "#5E9EA3", "#86B4B7"]
MAGMAS = [S.QUANTUM_DEEP, S.QUANTUM, "#6A1C81", "#E0455F"]
# Nested query windows around the anchor: (half side as a share of the tile, half duration as a share of the
# cube window). The innermost one is the window whose records are used as the analytical background.
WINDOWS = [(0.24, 0.30), (0.15, 0.19), (0.08, 0.10)]


def export(draw, name, w_mm, h_mm):
    """Draw one part on its own canvas and save it as editable SVG and transparent 1,000 dpi PNG.

    Every part module exposes draw(ax) so that the assembly script can place
    the same drawing at the same physical size in the full figure.
    """
    S.apply()
    fig = plt.figure(figsize=(w_mm * S.MM, h_mm * S.MM))
    result = draw(fig.add_axes([0, 0, 1, 1]))
    for suffix, kwargs in [("svg", {}), ("png", {"dpi": 1000})]:
        staged_save(fig, OUT / f"{name}.{suffix}", transparent=True, **kwargs)
    plt.close(fig)
    return result


def staged_save(fig, path, **kwargs):
    """Save through a local temporary file: a synced or network folder can briefly lock a file open in a viewer."""
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / path.name
        fig.savefig(staged, **kwargs)
        for attempt in range(6):
            try:
                shutil.copyfile(staged, path)
                return
            except OSError:
                if attempt == 5:
                    raise
                time.sleep(2)


@lru_cache(maxsize=1)
def traces():
    """Trace segments as (n, 3) arrays of x, y in metres from the tile centre and t in seconds of the day."""
    data = json.loads((S.SOURCE / "basemap" / "rome_traces.json").read_text())
    return tuple(np.asarray(t, float) for t in data["traces"])


def runs(mask):
    """Start and stop indices of consecutive True runs."""
    edges = np.flatnonzero(np.diff(np.r_[0, mask.astype(int), 0]))
    return list(zip(edges[::2], edges[1::2]))


def window_pieces(paths, lo, hi, min_points=20):
    """Pieces of each trace inside the tile and the time interval [lo, hi]."""
    out = []
    for p in paths:
        keep = (p[:, 2] >= lo) & (p[:, 2] <= hi) & (np.abs(p[:, 0]) <= HALF) & (np.abs(p[:, 1]) <= HALF)
        out += [p[a:b] for a, b in runs(keep) if b - a >= min_points]
    return out


def is_moving(piece, max_still=0.6, still_speed=1.0):
    """True when the taxi is stationary (below `still_speed` m/s) for at most `max_still` of the piece's
    duration; mostly stationary pieces are taxi-rank waits."""
    dt = np.diff(piece[:, 2])
    speed = np.hypot(*np.diff(piece[:, :2], axis=0).T) / np.maximum(dt, 1.0)
    return dt[speed < still_speed].sum() <= max_still * dt.sum()


@lru_cache(maxsize=4)
def anchor(cell=400.0, reach=1200.0):
    """Centre of the cell near the tile centre crossed by the most distinct moving traces in the middle
    ten minutes of the cube window."""
    lo, hi = CUBE_WINDOW_S
    mid = (lo + hi) / 2
    edges = np.arange(-reach, reach + cell, cell)
    counts = np.zeros((len(edges) - 1, len(edges) - 1))
    for p in filter(is_moving, window_pieces(traces(), lo, hi)):
        q = p[(p[:, 2] >= mid - 300) & (p[:, 2] <= mid + 300), :2]
        hist, _, _ = np.histogram2d(q[:, 0], q[:, 1], bins=[edges, edges])
        counts += hist > 0
    i, j = np.unravel_index(counts.argmax(), counts.shape)
    return np.array([edges[i] + cell / 2, edges[j] + cell / 2])
