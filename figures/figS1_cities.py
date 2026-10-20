"""Supplementary Figure S1: the ten sources not enlarged in Figure 2.

Same layers, extent, colour scales and symbols as Figure 2(c)-(f), so every
source can be compared on one visual scale. With the v1 density grids Dublin
and Brighton show no density layer because no cell passes the entity
disclosure rule; the v2 grids used by the current figures show every nonempty
cell (see build_tables_geography.py).
"""
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import numpy as np

import maps as M
import style as S

S.apply()
geo, anc = M.geometry(), M.anchors()
ORDER = [("geolife", "Beijing (GeoLife)"), ("jinan", "Jinan"), ("dublin", "Dublin"), ("porto", "Porto"),
         ("montreal", "Montréal"), ("barcelona", "Barcelona"), ("stellenbosch", "Stellenbosch"),
         ("nyc_mat", "New York City"), ("paris_mat", "Paris"), ("brighton_shl", "Brighton")]
assert len(ORDER) == 10 and not {s for s, _ in ORDER} & {"tdrive", "rome_taxi", "sf_cabspotting", "rio"}
density_max = max(np.nanmax(M.density(s, geo[s])[0]) for s in geo if np.isfinite(M.density(s, geo[s])[0]).any())
density_norm = Normalize(0, np.ceil(density_max))

fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 108 * S.MM))
gs = fig.add_gridspec(2, 5, left=0.012, right=0.988, top=0.94, bottom=0.17, wspace=0.05, hspace=0.12)
axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(5)]
for ax, (sid, name) in zip(axes, ORDER):
    M.city_map(ax, sid, geo[sid], anc[anc.source_id.eq(sid)], density_norm, name, zoom=12)

fig.canvas.draw()
cax1 = fig.add_axes([0.05, 0.065, 0.22, 0.016])
cax2 = fig.add_axes([0.36, 0.065, 0.22, 0.016])
cb1 = fig.colorbar(plt.cm.ScalarMappable(norm=M.SHARE_NORM, cmap=M.SHARE_CMAP), cax=cax1,
                   orientation="horizontal", ticks=[0, 5, 10, 15, 20], extend="max")
cb2 = fig.colorbar(plt.cm.ScalarMappable(norm=density_norm, cmap=M.DENSITY), cax=cax2,
                   orientation="horizontal", ticks=range(int(density_norm.vmax) + 1))
for cb, label in [(cb1, "Windows with Q < C (%)"), (cb2, "Records per km² (log₁₀)")]:
    cb.outline.set_linewidth(0.4)
    cb.ax.tick_params(labelsize=6.2, length=1.5, width=0.4, pad=1)
    cb.ax.xaxis.set_label_position("top")
    cb.set_label(label, fontsize=6.5, labelpad=3)
leg_ax = fig.add_axes([0.64, 0.02, 0.35, 0.11])
leg_ax.set_axis_off()
leg_ax.legend(handles=[
    Line2D([], [], ls="none", marker="o", ms=4.5, markerfacecolor=S.QUANTUM, markeredgecolor="white", label="Anchor with Q < C windows"),
    Line2D([], [], ls="none", marker="o", ms=4.5, markerfacecolor="white", markeredgecolor=S.GREY, label="No window with Q < C"),
    Line2D([], [], ls="none", marker="x", ms=3.8, color=S.GREY, label="No eligible window")],
    loc="center left", ncol=1, frameon=False, handletextpad=0.5, labelspacing=0.7)
for ax, letter in zip(axes, "abcdefghij"):
    S.panel_label(ax, letter, dx_pt=0, dy_pt=3)

S.save(fig, "figureS1_cities", exclude_axes=[cax1, cax2, leg_ax],
       accepted_overlaps={name: "map label with white box over basemap" for _, name in ORDER} | {"5 km": "scale label with white halo"})
