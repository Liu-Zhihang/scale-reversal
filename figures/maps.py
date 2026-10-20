"""Map layers shared by Figure 2 and Supplementary Figure S1.

City maps are drawn in each source's registered UTM zone, 24 km wide and centred
on its reference point, the same extent as the privacy-suppressed density grids.
The street basemap is Esri World Light Gray Canvas (Esri and its data providers); the
world and Europe maps use Natural Earth 1:50m land and country polygons, stored
in SR_FIGURE_DATA/basemap. Downloaded tiles are cached in SR_TILE_CACHE.
"""
from collections import Counter
import functools
import json

import contextily as ctx
import geopandas as gpd
import numpy as np
import pandas as pd
from matplotlib import patheffects
from matplotlib.colors import LinearSegmentedColormap, Normalize

import paths as P
import style as S

M1_INPUTS = S.EVIDENCE / "cities_context_perturbation_20260921_v1r1" / "inputs"
BASEMAP = S.SOURCE / "basemap"
ctx.set_cache_dir(str(P.tile_cache()))
TILES = ctx.providers.Esri.WorldGrayCanvas
HALF_M = 12000                        # half width of every city map and grid
ANCHOR_STEP_M = 20000 / 3             # anchor offsets: -1, 0, +1 steps

LAND = "#E8E5E0"
BORDER = "#FFFFFF"
# Opacity rises with density so sparse cells barely tint the basemap.
DENSITY = LinearSegmentedColormap.from_list(
    "density", [(0.78, 0.87, 0.87, 0.20), (0.50, 0.70, 0.72, 0.48), (0.22, 0.49, 0.52, 0.78), (0.07, 0.25, 0.27, 0.93)])
HALO = [patheffects.withStroke(linewidth=1.8, foreground="white")]
SHARE_NORM = Normalize(0, 20)         # % of windows with Q < C; anchors above 20 saturate
SHARE_CMAP = S.WARM_STRONG
CITY_NAME = {**S.SOURCE_LABEL, "tdrive": "Beijing", "geolife": "Beijing", "nyc_mat": "New York City",
             "paris_mat": "Paris", "brighton_shl": "Brighton"}
# Monitoring-only settings are not in the access cohort and have no registered
# reference point; they are placed at their city coordinates.
MONITORING_ONLY = {"Zurich": (47.3769, 8.5417), "Portici": (40.8197, 14.3411)}


def geometry():
    """Registered reference point and UTM zone of every access source."""
    rows = json.loads((M1_INPUTS / "geometry_qa.json").read_text())
    return {r["source_id"]: dict(epsg=int(r["epsg"]), x=r["reference"]["x"], y=r["reference"]["y"],
                                 lat=float(r["reference"]["reference_lat"]),
                                 lon=float(r["reference"]["reference_lon"])) for r in rows}


def records():
    """Registered point records per source, summed over its source-days."""
    total = Counter()
    for case in json.loads((M1_INPUTS / "cases.json").read_text()):
        total[case["source_id"]] += case["n"]
    return total


def anchors():
    return pd.read_csv(S.SOURCE / "figure2_anchor_counts.csv", dtype={"anchor": str})


def density(sid, geo):
    """log10 records per km2 on the suppressed grid; NaN where suppressed or empty."""
    g = json.loads((S.SOURCE / "density_grids" / f"{sid}.json").read_text())
    assert np.allclose(g["origin_xy"], [geo["x"] - HALF_M, geo["y"] - HALF_M])
    field = np.array([np.nan if v is None else v for v in g["counts"]], dtype=float).reshape(g["shape"])
    return np.log10(field / (g["cell_m"] / 1000) ** 2), g


def world_layers(crs):
    land = gpd.read_file(BASEMAP / "ne_50m_land.geojson").clip_by_rect(-180, -57, 180, 84).to_crs(crs)
    borders = gpd.read_file(BASEMAP / "ne_50m_admin_0_countries.geojson").boundary.to_crs(crs)
    return land, borders


def fit_limits(ax, xmin, xmax, ymin, ymax):
    """Expand a projected box to the axes aspect so equal scaling fills the panel."""
    bbox = ax.get_position()
    fig_w, fig_h = ax.figure.get_size_inches()
    target = (bbox.height * fig_h) / (bbox.width * fig_w)
    w, h = xmax - xmin, ymax - ymin
    if h / w < target:
        pad = (w * target - h) / 2
        ymin, ymax = ymin - pad, ymax + pad
    else:
        pad = (h / target - w) / 2
        xmin, xmax = xmin - pad, xmax + pad
    return xmin, xmax, ymin, ymax


def project(lonlat, crs):
    lon, lat = zip(*lonlat)
    pts = gpd.GeoSeries(gpd.points_from_xy(lon, lat), crs=4326).to_crs(crs)
    return np.c_[pts.x, pts.y]


def city_map(ax, sid, geo, anchor_rows, density_norm, label, zoom=13):
    """Street basemap, observation density and the nine registered anchors."""
    cx, cy = geo["x"], geo["y"]
    ax.set_xlim(cx - HALF_M, cx + HALF_M)
    ax.set_ylim(cy - HALF_M, cy + HALF_M)
    ax.set_aspect("equal", adjustable="box")
    ctx.add_basemap(ax, crs=f"EPSG:{geo['epsg']}", source=TILES, zoom=zoom, attribution=False,
                    reset_extent=True, zorder=0)
    field, grid = density(sid, geo)
    if np.isfinite(field).any():
        ax.imshow(np.ma.masked_invalid(field), origin="lower", cmap=DENSITY, norm=density_norm,
                  extent=(cx - HALF_M, cx + HALF_M, cy - HALF_M, cy + HALF_M), interpolation="nearest", zorder=1)
    for r in anchor_rows.itertuples():
        x, y = cx + (r.ix - 1) * ANCHOR_STEP_M, cy + (r.iy - 1) * ANCHOR_STEP_M
        if r.nonempty_supported == 0:
            ax.scatter(x, y, s=14, marker="x", color=S.GREY, linewidths=0.8, zorder=3)
        elif r.lower == 0:
            ax.scatter(x, y, s=32, facecolors="white", edgecolors=S.GREY, linewidths=0.8, zorder=3)
        else:
            ax.scatter(x, y, s=38, color=SHARE_CMAP(SHARE_NORM(100 * r.fraction)), edgecolors="white",
                       linewidths=0.7, zorder=3)
    bar_x, bar_y = cx - HALF_M + 1500, cy - HALF_M + 1500
    ax.plot([bar_x, bar_x + 5000], [bar_y, bar_y], color=S.INK, lw=1.2, solid_capstyle="butt", zorder=4)
    ax.text(bar_x + 2500, bar_y + 500, "5 km", ha="center", va="bottom", fontsize=6.2, color=S.INK, zorder=4,
            path_effects=HALO)
    ax.text(cx - HALF_M + 1200, cy + HALF_M - 1200, label, ha="left", va="top", fontsize=7, color=S.INK,
            fontweight="bold", zorder=4,
            bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8))
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(True)
        side.set_color(S.MID_GREY)
        side.set_linewidth(0.5)
    return grid

# ---- OpenStreetMap layers for the Figure 1 parts ---------------------------
OSM_WIDTH = {"motorway": 1.6, "trunk": 1.5, "primary": 1.25, "secondary": 1.0, "tertiary": 0.8,
             "unclassified": 0.5, "residential": 0.45, "living_street": 0.35, "pedestrian": 0.35}
OSM_BLOCK, OSM_PARK, OSM_WATER, OSM_STREET = "#ECEAE6", "#E2E5DE", "#D5E2E5", "#FFFFFF"


@functools.lru_cache(maxsize=1)
def rome_osm_layers():
    """Streets by class, river centrelines, parks and water in metres from the Rome tile centre."""
    import pyproj
    geo = geometry()["rome_taxi"]
    to_m = pyproj.Transformer.from_crs(4326, geo["epsg"], always_xy=True)
    osm = json.loads((BASEMAP / "rome_osm.json").read_text())
    cx, cy = osm["tile"]["centre_xy"]
    layers = {"streets": {k: [] for k in OSM_WIDTH}, "river": [], "parks": [], "water": []}
    for el in osm["elements"]:
        if "geometry" not in el:
            continue
        x, y = to_m.transform([p["lon"] for p in el["geometry"]], [p["lat"] for p in el["geometry"]])
        xy = np.c_[np.asarray(x) - cx, np.asarray(y) - cy]
        tags = el.get("tags", {})
        if tags.get("leisure") == "park" and len(xy) > 3:
            layers["parks"].append(xy)
        elif tags.get("natural") == "water" and len(xy) > 3:
            layers["water"].append(xy)
        elif tags.get("waterway") == "river":
            layers["river"].append(xy)
        elif tags.get("highway") in OSM_WIDTH:
            layers["streets"][tags["highway"]].append(xy)
    return layers
