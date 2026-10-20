"""Figure 1 part: the analytical background around a held-out target (vector).

A 1.8 km square of the same Rome street map, centred on the cube's query
anchor. Records from the cube's innermost time slice (the anchor time plus or
minus 4 min) are plotted as points: those inside the dashed query window, the
innermost prism's footprint, are the background passed to the urban task and
are drawn in observation teal; the rest are pale grey. The held-out target
sits at the anchor. Exported as editable SVG and a transparent 1,000 dpi PNG.
Basemap data (c) OpenStreetMap contributors, ODbL.
"""
import numpy as np

import fig1_part_city as city
import fig1_parts_common as C
import maps as M
import style as S

TILE = 900.0                                    # half side of this tile in metres
STREET_SCALE = 2.0                              # wider streets at this zoom
SIZE_MM = 40.0
LO, HI = C.CUBE_WINDOW_S


def draw(ax):
    hw, ht = C.WINDOWS[-1]
    win = hw * 2 * C.HALF                       # half side of the query window in metres
    half_s = ht * (HI - LO)                     # half duration of the query window in seconds
    anchor_xy = C.anchor()
    mid = (LO + HI) / 2
    recs = np.vstack([p[np.abs(p[:, 2] - mid) <= half_s, :2] for p in C.traces()]) - anchor_xy
    recs = recs[(np.abs(recs[:, 0]) <= TILE) & (np.abs(recs[:, 1]) <= TILE)][::3]
    inside = (np.abs(recs[:, 0]) <= win) & (np.abs(recs[:, 1]) <= win)

    city.street_map(ax, M.rome_osm_layers(), shift=anchor_xy, scale=STREET_SCALE, extent=TILE)
    ax.scatter(*recs[~inside].T, s=3.2, color="#BFC4C7", edgecolors="none", zorder=3)
    ax.scatter(*recs[inside].T, s=4.5, color=S.CLASSICAL, edgecolors="white", linewidths=0.2, zorder=4)
    ax.plot([-win, win, win, -win, -win], [-win, -win, win, win, -win], color=S.INK, lw=0.8,
            ls=(0, (3.0, 2.0)), zorder=5)
    ax.scatter([0], [0], s=30, color=S.INK, edgecolors="white", linewidths=0.7, zorder=6)
    city.frame(ax, TILE)
    return {"records": len(recs), "inside": int(inside.sum())}


if __name__ == "__main__":
    print("part4_background", C.export(draw, "part4_background", SIZE_MM, SIZE_MM))
