"""Figure 1 part: city-scale trajectories on a light street map (vector).

A 6 km square centred on the densest taxi trajectories in central Rome:
OpenStreetMap streets, river and parks drawn as vector shapes, and real taxi
trajectories from 07:00 to 09:00 on 2014-02-21 (records at most 120 s and
800 m apart are joined), in the paper's observation teal with a few records
marked in the quantum colour. Exported as editable SVG and a transparent
1,000 dpi PNG. Basemap data (c) OpenStreetMap contributors, ODbL.
"""
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Polygon
import numpy as np
from shapely.geometry import LineString, Polygon as ShapelyPolygon, box

import fig1_parts_common as C
import maps as M
import style as S

HALF = C.HALF
SIZE_MM = 50.0


def clip(shapes, shift, extent, area=False):
    """Clip polylines (or polygons when `area`) in metres to the square tile, so that nothing outside it
    survives in the vector output."""
    window = box(-extent, -extent, extent, extent)
    out = []
    for xy in shapes:
        geom = (ShapelyPolygon(xy - shift).buffer(0) if area else LineString(xy - shift)).intersection(window)
        for part in getattr(geom, "geoms", [geom]):
            if part.is_empty:
                continue
            if area and part.geom_type == "Polygon":
                out.append(np.asarray(part.exterior.coords))
            elif not area and part.geom_type == "LineString":
                out.append(np.asarray(part.coords))
    return out


def street_map(ax, layers, shift=(0.0, 0.0), scale=1.0, extent=HALF):
    """Light OpenStreetMap layers in metres, shifted so that `shift` sits at the origin and clipped to the tile."""
    s = np.asarray(shift)
    ax.add_patch(Polygon([(-extent, -extent), (extent, -extent), (extent, extent), (-extent, extent)],
                         closed=True, facecolor=M.OSM_BLOCK, edgecolor="none", zorder=0))
    for key, color in [("parks", M.OSM_PARK), ("water", M.OSM_WATER)]:
        for xy in clip(layers[key], s, extent, area=True):
            ax.add_patch(Polygon(xy, closed=True, facecolor=color, edgecolor="none", zorder=1))
    ax.add_collection(LineCollection(clip(layers["river"], s, extent), colors=M.OSM_WATER,
                                     linewidths=4.0 * scale, capstyle="butt", zorder=1))
    for kind in sorted(M.OSM_WIDTH, key=M.OSM_WIDTH.get):
        ax.add_collection(LineCollection(clip(layers["streets"][kind], s, extent), colors=M.OSM_STREET,
                                         linewidths=scale * M.OSM_WIDTH[kind], capstyle="butt",
                                         joinstyle="round", zorder=2))


def frame(ax, extent):
    """Square limits, light outline and no axes."""
    ax.add_patch(Polygon([(-extent, -extent), (extent, -extent), (extent, extent), (-extent, extent)],
                         closed=True, facecolor="none", edgecolor="#C9CCCE", lw=0.6, zorder=7))
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_aspect("equal")
    ax.set_axis_off()


def draw(ax):
    street_map(ax, M.rome_osm_layers())
    paths = [p[:, :2] for p in C.traces()]
    rng = np.random.default_rng(3)
    shade = [to_rgba(C.TEALS[i], 0.78) for i in rng.integers(len(C.TEALS), size=len(paths))]
    ax.add_collection(LineCollection(paths, colors=shade, linewidths=0.5, capstyle="round", joinstyle="round",
                                     zorder=3))
    inside = [p[(np.abs(p[:, 0]) < 0.85 * HALF) & (np.abs(p[:, 1]) < 0.85 * HALF)] for p in paths]
    inside = [p for p in inside if len(p)]
    picks = np.vstack([inside[k][rng.integers(len(inside[k]))] for k in rng.choice(len(inside), 22, replace=False)])
    ax.scatter(picks[:, 0], picks[:, 1], s=6, color=S.QUANTUM, edgecolors="white", linewidths=0.35, zorder=4)
    frame(ax, HALF)


if __name__ == "__main__":
    C.export(draw, "part2_city_trajectories", SIZE_MM, SIZE_MM)
    print("wrote part2_city_trajectories")
