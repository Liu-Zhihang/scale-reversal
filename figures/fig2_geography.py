"""Figure 2: where the observations are, globally and inside four cities.

Figure contract
- Claim: the cohort spans 13 cities on five continents with very different
  observation systems, and inside each city the windows where quantum filtering
  costs less sit where supported observations are dense, at the reference centre
  in some cities (Rome, San Francisco) and off it in others (Beijing, Rio).
- (a) context: the 13 access cities on a world map, coloured by their share of
  windows with Q < C; the two monitoring-only settings are marked separately.
- (b) the European cities, which overlap at world scale.
- (c)-(f) four cities on a street basemap: pooled observation density and the
  nine registered anchors, coloured by their share of windows with Q < C.
The other ten sources are drawn identically in Supplementary Fig. S1.
"""
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import numpy as np

import maps as M
import style as S

S.apply()
geo, rec, anc = M.geometry(), M.records(), M.anchors()
assert anc.lower.sum() == 742 and anc.nonempty_supported.sum() == 13370
assert sum(rec.values()) == 101_240_625 and len(geo) == 14

anc["city"] = anc.source_id.map(M.CITY_NAME)
city = anc.groupby("city")[["lower", "nonempty_supported"]].sum()
city["share"] = 100 * city.lower / city.nonempty_supported
assert len(city) == 13
lonlat = {M.CITY_NAME[s]: (g["lon"], g["lat"]) for s, g in geo.items()}
KEY = [("tdrive", "Beijing"), ("rome_taxi", "Rome"), ("sf_cabspotting", "San Francisco"), ("rio", "Rio de Janeiro")]
key_cities = {name for _, name in KEY}
EUROPE = (-11.5, 35.5, 19.5, 56.8)   # lon/lat box enlarged in (b)
density_max = max(np.nanmax(M.density(s, geo[s])[0]) for s in geo if np.isfinite(M.density(s, geo[s])[0]).any())
density_norm = Normalize(0, np.ceil(density_max))

# ---- Layout ----------------------------------------------------------------
fig = plt.figure(figsize=(S.FULL_WIDTH_MM * S.MM, 150 * S.MM))
top = fig.add_gridspec(1, 2, width_ratios=[2.08, 1], left=0.012, right=0.988, top=0.935, bottom=0.53, wspace=0.03)
bottom = fig.add_gridspec(1, 4, left=0.012, right=0.988, top=0.455, bottom=0.115, wspace=0.05)
ax_w, ax_e = fig.add_subplot(top[0, 0]), fig.add_subplot(top[0, 1])
city_axes = [fig.add_subplot(bottom[0, j]) for j in range(4)]


def city_points(ax, crs, names, label_offsets):
    """Access cities as filled circles, monitoring-only settings as diamonds."""
    access = [n for n in names if n in city.index]
    xy = M.project([lonlat[n] for n in access], crs)
    for (x, y), name in zip(xy, access):
        share = city.loc[name, "share"]
        face = M.SHARE_CMAP(M.SHARE_NORM(share)) if share > 0 else "white"
        ax.scatter(x, y, s=34, facecolors=face, edgecolors=S.GREY if share == 0 else "white",
                   linewidths=0.8 if share == 0 else 0.6, zorder=4)
        if name in key_cities:
            ax.scatter(x, y, s=95, facecolors="none", edgecolors=S.INK, linewidths=0.7, zorder=4)
    mon = [n for n in names if n in M.MONITORING_ONLY]
    if mon:
        mxy = M.project([M.MONITORING_ONLY[n][::-1] for n in mon], crs)
        ax.scatter(mxy[:, 0], mxy[:, 1], s=26, marker="D", facecolors="white", edgecolors=S.CLASSICAL,
                   linewidths=0.9, zorder=4)
        xy = np.vstack([xy, mxy]) if len(xy) else mxy
        access = access + mon
    for (x, y), name in zip(xy, access):
        if name not in label_offsets:
            continue
        dx, dy, ha = label_offsets[name]
        ax.annotate(name, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                    fontsize=6.5, color=S.INK, fontweight="bold" if name in key_cities else "normal", zorder=5,
                    path_effects=M.HALO)


# ---- (a) world -------------------------------------------------------------
WORLD = "EPSG:8857"
land, borders = M.world_layers(WORLD)
land.plot(ax=ax_w, color=M.LAND, linewidth=0, zorder=1)
borders.plot(ax=ax_w, color=M.BORDER, linewidth=0.3, zorder=2)
box = np.array([(EUROPE[0], EUROPE[1]), (EUROPE[2], EUROPE[1]), (EUROPE[2], EUROPE[3]),
                (EUROPE[0], EUROPE[3]), (EUROPE[0], EUROPE[1])])
edge = np.vstack([np.linspace(box[i], box[i + 1], 40) for i in range(4)])
exy = M.project(edge, WORLD)
ax_w.plot(exy[:, 0], exy[:, 1], color=S.GREY, lw=0.6, ls=(0, (3, 2)), zorder=3)
outside = [n for n in city.index if not (EUROPE[0] <= lonlat[n][0] <= EUROPE[2] and EUROPE[1] <= lonlat[n][1] <= EUROPE[3])]
city_points(ax_w, WORLD, outside, {
    "Beijing": (-6, 5, "right"), "Jinan": (6, -3, "left"), "San Francisco": (-6, 0, "right"),
    "Montréal": (-3, 6, "right"), "New York City": (6, -3, "left"), "Rio de Janeiro": (6, 0, "left"),
    "Stellenbosch": (6, 0, "left")})
xmin, ymin, xmax, ymax = land.total_bounds
ax_w.set_xlim(xmin, xmax)
ax_w.set_ylim(ymin, ymax)
ax_w.set_aspect("equal", adjustable="datalim")
ax_w.set_axis_off()

# ---- (b) Europe ------------------------------------------------------------
EU = "EPSG:3035"
bxy = M.project(edge, EU)
ex0, ex1, ey0, ey1 = M.fit_limits(ax_e, bxy[:, 0].min(), bxy[:, 0].max(), bxy[:, 1].min(), bxy[:, 1].max())
land_e, borders_e = M.world_layers(EU)
# Clip to the visible box so no geometry outside the panel survives in the export.
land_e.clip_by_rect(ex0, ey0, ex1, ey1).plot(ax=ax_e, color=M.LAND, linewidth=0, zorder=1)
borders_e.clip_by_rect(ex0, ey0, ex1, ey1).plot(ax=ax_e, color=M.BORDER, linewidth=0.4, zorder=2)
city_points(ax_e, EU, [n for n in city.index if n not in outside] + list(M.MONITORING_ONLY), {
    "Dublin": (-6, 3, "right"), "Brighton": (6, -2, "left"), "Paris": (6, 2, "left"),
    "Porto": (-6, 0, "right"), "Barcelona": (6, -3, "left"), "Rome": (-6, 4, "right"),
    "Zurich": (6, 3, "left"), "Portici": (6, -4, "left")})
ax_e.set_xlim(ex0, ex1)
ax_e.set_ylim(ey0, ey1)
ax_e.set_aspect("equal", adjustable="datalim")
ax_e.set_xticks([])
ax_e.set_yticks([])
for side in ax_e.spines.values():
    side.set_visible(True)
    side.set_color(S.GREY)
    side.set_linewidth(0.6)
    side.set_linestyle((0, (3, 2)))

# ---- (c)-(f) four cities ---------------------------------------------------
for ax, (sid, name) in zip(city_axes, KEY):
    M.city_map(ax, sid, geo[sid], anc[anc.source_id.eq(sid)], density_norm, name)

# ---- Keys and panel letters ------------------------------------------------
fig.canvas.draw()
cax1 = fig.add_axes([0.05, 0.055, 0.22, 0.011])
cax2 = fig.add_axes([0.36, 0.055, 0.22, 0.011])
cb1 = fig.colorbar(plt.cm.ScalarMappable(norm=M.SHARE_NORM, cmap=M.SHARE_CMAP), cax=cax1,
                   orientation="horizontal", ticks=[0, 5, 10, 15, 20], extend="max")
cb2 = fig.colorbar(plt.cm.ScalarMappable(norm=density_norm, cmap=M.DENSITY), cax=cax2,
                   orientation="horizontal", ticks=range(int(density_norm.vmax) + 1))
for cb, label in [(cb1, "Windows with Q < C (%)"), (cb2, "Records per km² (log₁₀)")]:
    cb.outline.set_linewidth(0.4)
    cb.ax.tick_params(labelsize=6.2, length=1.5, width=0.4, pad=1)
    cb.ax.xaxis.set_label_position("top")
    cb.set_label(label, fontsize=6.5, labelpad=3)
leg_ax = fig.add_axes([0.64, 0.015, 0.35, 0.085])
leg_ax.set_axis_off()
leg_ax.legend(handles=[
    Line2D([], [], ls="none", marker="o", ms=4.5, markerfacecolor=S.QUANTUM, markeredgecolor="white", label="Access city or anchor"),
    Line2D([], [], ls="none", marker="o", ms=4.5, markerfacecolor="white", markeredgecolor=S.GREY, label="No window with Q < C"),
    Line2D([], [], ls="none", marker="D", ms=3.8, markerfacecolor="white", markeredgecolor=S.CLASSICAL, label="Monitoring task only"),
    Line2D([], [], ls="none", marker="x", ms=3.8, color=S.MID_GREY, label="No eligible window")],
    loc="center left", ncol=2, frameon=False, handletextpad=0.5, columnspacing=2.2, labelspacing=0.9)
for ax, letter in zip([ax_w, ax_e, *city_axes], "abcdef"):
    S.panel_label(ax, letter, dx_pt=0, dy_pt=3)

map_labels = {*city.index, *M.MONITORING_ONLY, "5 km"}
S.save(fig, "figure2_observation_geography", exclude_axes=[cax1, cax2, leg_ax],
       accepted_overlaps={t: "map label with white halo over basemap, borders or density" for t in map_labels})
