"""Figure 1: one space-time window, two decisions (assembled vector figure).

Places the Figure 1 parts (fig1_part_*.py) at their physical sizes on a
190 mm canvas and adds section headings, flow arrows, zoom lines from Rome on
the world map to the city tile, and the vermilion dashed arrow for the risk
of choosing a background because it lowers access cost.

Layout, top band: urban observations (world map, Rome tile) -> space-time
windows (cube) -> analytical background (tile, estimate, error pair) ->
evaluation checklist. Bottom band: access routes (nested windows, index,
two routes to |S1>) -> scale reversal -> checklist.

Writes figure1_framework.png to SR_FIGURE_OUT through style.save (1,000 dpi,
font and collision audits) and an editable PDF and SVG (figure1_assembled.*)
to SR_FIGURE_OUT/figure1_parts.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

import fig1_part_background as background
import fig1_part_checklist as checklist
import fig1_part_city as city
import fig1_part_cube as cube
import fig1_part_estimate as estimate
import fig1_part_index as index
import fig1_part_reversal as reversal
import fig1_part_routes as routes
import fig1_part_windows as windows
import fig1_part_world as world
import fig1_parts_common as C
import style as S

W, H = 190.0, 126.0
HEADING_PT = 7.5

S.apply()
fig = plt.figure(figsize=(W * S.MM, H * S.MM))


def place(x, y, w, h):
    """Axes at x, y (top-left corner, mm from the top-left of the canvas) with size w x h mm."""
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


# ---- Parts at their physical sizes (mm) ------------------------------------------
world_h = world.height_mm(50.0)
ax_world = place(2, 8, 50, world_h)
rome = world.draw(ax_world)
city.draw(place(6, 33, 42, 42))
cube.draw(place(58, 7, *cube.SIZE_MM))
background.draw(place(126, 8, 34, 34))
estimate.draw_estimate(place(165, 13, *estimate.ESTIMATE_MM))
estimate.draw_error_pair(place(165, 28, *estimate.PAIR_MM))
checklist.draw_checklist(place(162, 47, *checklist.CHECK_MM))
windows.draw(place(2, 93, 44, 44 * windows.SIZE_MM[1] / windows.SIZE_MM[0]))
index.draw(place(50, 95, 46, 46 * index.SIZE_MM[1] / index.SIZE_MM[0]))
routes.draw(place(99, 90, 46, 46 * routes.SIZE_MM[1] / routes.SIZE_MM[0]))
reversal.draw(place(150, 87, *reversal.SIZE_MM))
checklist.draw_risk(place(143, 60, *checklist.RISK_MM))

# ---- Overlay in mm (y downwards) for headings, arrows and zoom lines -------------
ov = fig.add_axes([0, 0, 1, 1], zorder=10)
ov.set_xlim(0, W)
ov.set_ylim(H, 0)
ov.set_axis_off()
ov.patch.set_alpha(0)

for x, y, text in [(2, 2, "Urban observations"), (58, 2, "Space\u2013time windows"),
                   (126, 2, "Analytical background"), (2, 85, "Access routes"), (153, 83, "Scale reversal")]:
    ov.text(x, y, text, fontsize=HEADING_PT, fontweight="bold", color=S.INK, ha="left", va="top")


def flow(a, b, color=S.INK, rad=0.0, dashed=False, head=True, lw=0.8):
    ov.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>" if head else "-", mutation_scale=7, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0,
                                 linestyle=(0, (3.0, 2.0)) if dashed else "-"))


flow((49, 50), (57.5, 50))                      # Rome tile -> cube
flow((119.5, 30), (125.3, 30))                  # cube -> analytical background
flow((160.8, 18), (164.6, 18))                  # background -> estimate
flow((176, 23.3), (176, 27.6))                  # estimate -> error pair
flow((176, 40.5), (176, 46.5))                  # error pair -> checklist
flow((82, 79), (37.5, 96.5), rad=-0.15)             # cube -> nested windows
flow((46.5, 106), (49.6, 106))                  # nested windows -> index
flow((95.5, 104.75), (99.5, 104.75))             # index -> routes
flow((145, 107), (150.3, 107))                # routes -> scale reversal
flow((178, 86.8), (178, 81.7))                  # scale reversal -> checklist
flow((151, 95), (146.5, 66.6), color=S.RISK, dashed=True, head=False, lw=0.9)   # risk: cost -> background
flow((146.5, 59.8), (143, 42.8), color=S.RISK, dashed=True, lw=0.9)

# Zoom lines from Rome on the world map to the top corners of the Rome tile.
ax_world.apply_aspect()
rome_mm = ov.transData.inverted().transform(ax_world.transData.transform(rome))
for corner in [(6, 33), (48, 33)]:
    ov.plot([rome_mm[0], corner[0]], [rome_mm[1], corner[1]], color=S.MID_GREY, lw=0.45, zorder=0)

for suffix in ("pdf", "svg"):
    C.staged_save(fig, C.OUT / f"figure1_assembled.{suffix}")
S.save(fig, "figure1_framework", schematic=True)
