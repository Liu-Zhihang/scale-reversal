"""Figure 1 part: nested query windows around one anchor on a tilted slab (vector).

The three windows of the cube (same anchor, same half sides and durations)
seen as footprints on an isometric slab 3.6 km across. Points are real taxi
records within the outer window's time span; each is coloured by the
smallest window that contains it in space and time (innermost: quantum
colour, middle: observation teal, outer: grey, outside: pale). Window fills
and edges repeat the cube's prism colours. Exported as editable SVG and a
transparent 1,000 dpi PNG.
"""
from matplotlib.patches import Polygon
import numpy as np

import fig1_parts_common as C
import style as S

C30, S30 = np.cos(np.pi / 6), np.sin(np.pi / 6)
LO, HI = C.CUBE_WINDOW_S
MID = (LO + HI) / 2
EXTENT = 1800.0                                  # half side of the slab in metres
THICK = 0.035                                    # slab thickness in projected units
SIZE_MM = (56.0, 34.0)
FILLS = [("#E4ECEC", S.GREY), ("#CFE2E3", S.CLASSICAL), ("#F4CBD8", S.QUANTUM_DEEP)]
DOTS = ["#D3D6D8", S.MID_GREY, S.CLASSICAL, S.QUANTUM_DEEP]     # outside, outer, middle, inner


def P(u, v, t=0.0):
    """Isometric projection of slab coordinates u, v in [0, 1]; t lifts out of the slab."""
    u, v, t = np.broadcast_arrays(np.asarray(u, float), np.asarray(v, float), np.asarray(t, float))
    return np.stack([(u + v) * C30, (v - u) * S30 + t], axis=-1)


def unit(xy):
    """Metres from the anchor to slab coordinates."""
    return (np.asarray(xy) + EXTENT) / (2 * EXTENT)


def draw(ax):
    anchor_xy = C.anchor()
    half_m = [hw * 2 * C.HALF for hw, _ in C.WINDOWS]
    half_s = [ht * (HI - LO) for _, ht in C.WINDOWS]
    recs = np.vstack([p[np.abs(p[:, 2] - MID) <= half_s[0]] for p in C.traces()])
    recs[:, :2] -= anchor_xy
    recs = recs[(np.abs(recs[:, 0]) <= 0.97 * EXTENT) & (np.abs(recs[:, 1]) <= 0.97 * EXTENT)][::5]
    level = np.zeros(len(recs), int)
    for k, (hm, hs) in enumerate(zip(half_m, half_s), start=1):
        inside = (np.abs(recs[:, 0]) <= hm) & (np.abs(recs[:, 1]) <= hm) & (np.abs(recs[:, 2] - MID) <= hs)
        level[inside] = k

    # ---- Slab: top face and the two front faces --------------------------------
    for corners, face in [((P([0, 1, 1, 0], [0, 0, 1, 1])), "#F5F5F3"),
                          ((P([0, 1, 1, 0], [0, 0, 0, 0], [0, 0, -THICK, -THICK])), "#E2E2DF"),
                          ((P([1, 1, 1, 1], [0, 1, 1, 0], [0, 0, -THICK, -THICK])), "#D3D3D0")]:
        ax.add_patch(Polygon(corners, closed=True, facecolor=face, edgecolor=S.MID_GREY, lw=0.6,
                             joinstyle="round", zorder=0))
    # ---- Nested window footprints and records ------------------------------------
    for k, (hm, (face, edge)) in enumerate(zip(half_m, FILLS)):
        a, b = unit(-hm), unit(hm)
        ax.add_patch(Polygon(P([a, b, b, a], [a, a, b, b]), closed=True, facecolor=face, edgecolor=edge, lw=0.7,
                             joinstyle="miter", zorder=1 + k))
    for k, color in enumerate(DOTS):
        sel = recs[level == k]
        xy = P(unit(sel[:, 0]), unit(sel[:, 1]))
        ax.scatter(xy[:, 0], xy[:, 1], s=1.6 if k == 0 else 2.4, color=color, edgecolors="none", zorder=5 + k)
    ax.scatter(*P(0.5, 0.5), s=16, color=S.INK, edgecolors="white", linewidths=0.5, zorder=10)

    pts = P([0, 1, 1, 0, 1, 1], [0, 0, 1, 1, 0, 1], [0, 0, 0, 0, -THICK, -THICK])
    ax.set_xlim(pts[:, 0].min() - 0.02, pts[:, 0].max() + 0.02)
    ax.set_ylim(pts[:, 1].min() - 0.02, pts[:, 1].max() + 0.02)
    ax.set_aspect("equal")
    ax.set_axis_off()
    return {"records": len(recs), "by_level": np.bincount(level, minlength=4).tolist()}


if __name__ == "__main__":
    print("part7_nested_windows", C.export(draw, "part7_nested_windows", *SIZE_MM))
