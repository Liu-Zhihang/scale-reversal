"""Figure 1 part: global distribution of the 13 access cities (vector).

Natural Earth 1:50m land in the Equal Earth projection, light grey land and one
dark dot per access city at its registered reference point; Rome, the example
city of the next part, is ringed. Exported as an editable SVG and a
transparent 1,000 dpi PNG.
"""
import fig1_parts_common as C
import maps as M
import style as S

CRS = "EPSG:8857"
WIDTH_MM = 80.0


def layers():
    """Projected land, city reference points and Rome's position."""
    geo = M.geometry()
    cities = {}
    for g_id, g in geo.items():
        cities.setdefault(M.CITY_NAME[g_id], (g["lon"], g["lat"]))
    assert len(cities) == 13
    land, _ = M.world_layers(CRS)
    xy = M.project(list(cities.values()), CRS)
    rome = M.project([(geo["rome_taxi"]["lon"], geo["rome_taxi"]["lat"])], CRS)[0]
    return land, xy, rome


def height_mm(width_mm=WIDTH_MM):
    x0, y0, x1, y1 = layers()[0].total_bounds
    return width_mm * (y1 - y0) / (x1 - x0)


def draw(ax):
    """Draw the world map; return Rome's position in data coordinates."""
    land, xy, rome = layers()
    x0, y0, x1, y1 = land.total_bounds
    land.plot(ax=ax, color="#D3D1CC", linewidth=0)
    ax.scatter(xy[:, 0], xy[:, 1], s=9, color=S.INK, edgecolors="white", linewidths=0.4, zorder=3)
    ax.scatter([rome[0]], [rome[1]], s=34, facecolors="none", edgecolors=S.INK, linewidths=0.6, zorder=3)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.set_axis_off()
    return rome


if __name__ == "__main__":
    C.export(draw, "part1_world", WIDTH_MM, height_mm())
    print("wrote part1_world", f"{WIDTH_MM:.0f} x {height_mm():.0f} mm")
