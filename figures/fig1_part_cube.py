"""Figure 1 part: the space-time window as a time-geography cube (vector).

An isometric cube with equal x, y and t edges. Its floor is the same 6 km Rome
OpenStreetMap tile as the city part; its height is the 40 min from 07:40 to
08:20. Inside rise the real space-time paths of the taxi traces in the tile
during that interval (every GPS record kept): every trace stationary for at
most 60% of its duration plus six mostly stationary taxi-rank waits, so
moves lean and waver across the floor and stays rise vertically. Three nested,
translucent query prisms surround the cell crossed by the most moving traces;
the paths with most records in the innermost prism are drawn in the quantum
colours with their floor footprints, and each path through it is marked once
as a hit. Axes are added in the slide. Exported as editable SVG and a
transparent 1,000 dpi PNG. Basemap data (c) OpenStreetMap contributors, ODbL.
"""
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Circle, Polygon
import numpy as np

import fig1_parts_common as C
import maps as M
import style as S

HALF = C.HALF
LO, HI = C.CUBE_WINDOW_S
C30, S30 = np.cos(np.pi / 6), np.sin(np.pi / 6)
N_STAYS = 6                                     # taxi-rank waits kept as examples of stays
SIZE_MM = (61.0, 70.0)
PRISM_STYLE = [("#D9E7E7", 0.14, S.GREY), ("#C9DEDF", 0.18, S.CLASSICAL), ("#F2B8C9", 0.32, S.QUANTUM_DEEP)]


def P(u, v, t):
    """Isometric projection of floor coordinates u, v in [0, 1] and time t in [0, 1]."""
    u, v, t = np.broadcast_arrays(np.asarray(u, float), np.asarray(v, float), np.asarray(t, float))
    return np.stack([(u + v) * C30, (v - u) * S30 + t], axis=-1)


def to_unit(p):
    """Metres from the tile centre and seconds of the day to cube coordinates u, v, t in [0, 1]."""
    return np.c_[(p[:, 0] + HALF) / (2 * HALF), (p[:, 1] + HALF) / (2 * HALF), (p[:, 2] - LO) / (HI - LO)]


def floor_xy(xy):
    """Map metres from the tile centre to floor coordinates and project."""
    uv = (np.asarray(xy) + HALF) / (2 * HALF)
    return P(uv[:, 0], uv[:, 1], 0.0)


def clip_line(xy):
    """Pieces of a polyline inside the tile."""
    inside = (np.abs(xy[:, 0]) <= HALF) & (np.abs(xy[:, 1]) <= HALF)
    return [xy[a:b] for a, b in C.runs(inside) if b - a >= 2]


def edge(ax, a, b, color=S.MID_GREY, lw=0.6, z=3):
    ax.plot(*np.array([P(*a), P(*b)]).T, color=color, lw=lw, zorder=z, solid_capstyle="round")


def draw_floor(ax):
    ax.add_patch(Polygon(P([0, 1, 1, 0], [0, 0, 1, 1], 0), closed=True, facecolor=M.OSM_BLOCK, edgecolor="none",
                         zorder=0))
    layers = M.rome_osm_layers()
    for xy in layers["parks"] + layers["water"]:
        if np.all(np.abs(xy) <= HALF):
            ax.add_patch(Polygon(floor_xy(xy), closed=True, facecolor=M.OSM_PARK, edgecolor="none", zorder=1))
    river = [floor_xy(piece) for xy in layers["river"] for piece in clip_line(xy)]
    ax.add_collection(LineCollection(river, colors=M.OSM_WATER, linewidths=2.6, capstyle="round", zorder=1))
    for kind in sorted(M.OSM_WIDTH, key=M.OSM_WIDTH.get):
        segs = [floor_xy(piece) for xy in layers["streets"][kind] for piece in clip_line(xy)]
        ax.add_collection(LineCollection(segs, colors=M.OSM_STREET, linewidths=0.75 * M.OSM_WIDTH[kind],
                                         capstyle="round", zorder=2))


def draw_prisms(ax, au, av):
    """Nested translucent prisms: back faces behind the paths, front faces over them. Returns their bounds."""
    boxes = []
    for k, ((hw, ht), (face, alpha, ec)) in enumerate(zip(C.WINDOWS, PRISM_STYLE)):
        u0, u1, v0, v1, t0, t1 = au - hw, au + hw, av - hw, av + hw, 0.5 - ht, 0.5 + ht
        boxes.append((u0, u1, v0, v1, t0, t1))
        back = [[(u0, v1, t0), (u1, v1, t0), (u1, v1, t1), (u0, v1, t1)],
                [(u1, v0, t0), (u1, v1, t0), (u1, v1, t1), (u1, v0, t1)],
                [(u0, v0, t0), (u1, v0, t0), (u1, v1, t0), (u0, v1, t0)]]
        front = [[(u0, v0, t0), (u1, v0, t0), (u1, v0, t1), (u0, v0, t1)],
                 [(u0, v0, t0), (u0, v1, t0), (u0, v1, t1), (u0, v0, t1)],
                 [(u0, v0, t1), (u1, v0, t1), (u1, v1, t1), (u0, v1, t1)]]
        for faces, z in [(back, 4 + 0.1 * k), (front, 7.3 - 0.1 * k)]:
            for f in faces:
                ax.add_patch(Polygon(P(*np.array(f).T), closed=True, facecolor=to_rgba(face, alpha),
                                     edgecolor=to_rgba(ec, 0.9), lw=0.55, zorder=z))
    return boxes


def draw(ax):
    draw_floor(ax)
    for a, b in [((0, 1, 0), (0, 1, 1)), ((1, 1, 0), (1, 1, 1)), ((0, 0, 1), (0, 1, 1)), ((0, 1, 1), (1, 1, 1))]:
        edge(ax, a, b, z=3)
    for k in np.linspace(0.25, 0.75, 3):
        edge(ax, (0, 1, k), (1, 1, k), color=S.LIGHT_GREY, lw=0.4, z=2)
        edge(ax, (0, 0, k), (0, 1, k), color=S.LIGHT_GREY, lw=0.4, z=2)

    pieces = C.window_pieces(C.traces(), LO, HI)
    stays = [p for p in pieces if not C.is_moving(p)]
    keep = np.random.default_rng(11).choice(len(stays), min(N_STAYS, len(stays)), replace=False)
    paths = [p for p in pieces if C.is_moving(p)] + [stays[k] for k in sorted(keep)]
    au, av = (C.anchor() + HALF) / (2 * HALF)
    u0, u1, v0, v1, t0, t1 = draw_prisms(ax, au, av)[-1]

    # ---- Real space-time paths ------------------------------------------------
    unit = [to_unit(p) for p in paths]
    inside = [(q[:, 0] >= u0) & (q[:, 0] <= u1) & (q[:, 1] >= v0) & (q[:, 1] <= v1) & (q[:, 2] >= t0)
              & (q[:, 2] <= t1) for q in unit]
    order = np.argsort([-m.sum() for m in inside])
    lead = [k for k in order[:len(C.MAGMAS)] if inside[k].any()]
    rng = np.random.default_rng(5)
    rest = [k for k in range(len(unit)) if k not in lead]
    shade = [to_rgba(C.TEALS[i], 0.72) for i in rng.integers(len(C.TEALS), size=len(rest))]
    ax.add_collection(LineCollection([P(*unit[k].T) for k in rest], colors=shade, linewidths=0.42,
                                     capstyle="round", joinstyle="round", zorder=5))
    for color, k in zip(C.MAGMAS, lead):
        q = unit[k]
        ax.plot(*P(q[:, 0], q[:, 1], 0).T, color=to_rgba(color, 0.6), lw=0.45, zorder=3)
        ax.plot(*P(*q.T).T, color=color, lw=0.85, zorder=6, solid_capstyle="round", solid_joinstyle="round")
    for q, m in zip(unit, inside):
        if m.any():
            h = q[np.flatnonzero(m)[m.sum() // 2]]
            ax.add_patch(Circle(P(*h), 0.009, facecolor=S.QUANTUM_DEEP, edgecolor="white", lw=0.3, zorder=6.5))
    ax.add_patch(Circle(P(au, av, 0), 0.016, facecolor=S.INK, edgecolor="white", lw=0.4, zorder=3))

    for a, b in [((0, 0, 0), (1, 0, 0)), ((0, 0, 0), (0, 1, 0)), ((1, 0, 0), (1, 1, 0)), ((0, 1, 0), (1, 1, 0)),
                 ((0, 0, 0), (0, 0, 1)), ((1, 0, 0), (1, 0, 1)), ((0, 0, 1), (1, 0, 1)), ((1, 0, 1), (1, 1, 1))]:
        edge(ax, a, b, color=S.GREY, lw=0.7, z=10)
    pts = P([0, 1, 1, 0, 0, 1, 1, 0], [0, 0, 1, 1, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1, 1, 1])
    ax.set_xlim(pts[:, 0].min() - 0.02, pts[:, 0].max() + 0.02)
    ax.set_ylim(pts[:, 1].min() - 0.02, pts[:, 1].max() + 0.02)
    ax.set_aspect("equal")
    ax.set_axis_off()
    return {"paths": len(paths), "through_inner": int(sum(m.any() for m in inside))}


if __name__ == "__main__":
    print("part3_spacetime_cube", C.export(draw, "part3_spacetime_cube", *SIZE_MM))
