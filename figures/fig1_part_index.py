"""Figure 1 part: the spatio-temporal index as a fan-out-4 tree (vector, no text).

A root node, four internal nodes and sixteen leaf blocks, each node drawn as
a row of four entry slots, as in the paper's trees (fan-out 4); leaf blocks
carry three record rows. The query's traversal is drawn in ink: visited
entries are shaded and their child links are dark; leaf blocks reached by the
query are filled in observation teal. Unvisited structure is pale grey. The
layout is schematic. Exported as editable SVG and a transparent 1,000 dpi PNG.
"""
from matplotlib.patches import FancyBboxPatch, Rectangle

import fig1_parts_common as C
import style as S

FAN = 4
VISIT_ROOT = {1, 2}                              # root entries followed by the query
VISIT_INNER = {1: {2, 3}, 2: {0, 1, 2}}          # internal node -> entries followed
PALE, PALE_FILL, SLOT_HIT = "#C3C7CA", "#F3F4F4", "#D4E4E5"
SIZE_MM = (56.0, 30.0)
LEAF_W = 0.038                                   # leaves sit directly under their slots
LEAF_Y = 0.06


def node(ax, xc, y, w, h, hits, z=3):
    """Draw a node of FAN entry slots centred at xc; return the bottom-centre of each slot."""
    x0, sw = xc - w / 2, w / FAN
    visited = bool(hits)
    ax.add_patch(FancyBboxPatch((x0, y), w, h, boxstyle="round,pad=0,rounding_size=0.008", facecolor="white",
                                edgecolor=S.INK if visited else PALE, lw=0.7, zorder=z))
    ports = []
    for k in range(FAN):
        if k in hits:
            ax.add_patch(Rectangle((x0 + k * sw + 0.004, y + 0.004), sw - 0.008, h - 0.008, facecolor=SLOT_HIT,
                                   edgecolor="none", zorder=z + 0.1))
        if k:
            ax.plot([x0 + k * sw] * 2, [y, y + h], color=S.INK if visited else PALE, lw=0.45, zorder=z + 0.2)
        ports.append((x0 + (k + 0.5) * sw, y))
    return ports


def link(ax, a, b, on):
    ax.plot([a[0], a[0], b[0], b[0]], [a[1], (a[1] + b[1]) / 2, (a[1] + b[1]) / 2, b[1]],
            color=S.INK if on else PALE, lw=0.75 if on else 0.5, zorder=2 if on else 1,
            solid_joinstyle="miter", solid_capstyle="butt")


def leaf(ax, x, on):
    """A leaf block with three record rows; teal when the query reaches it."""
    ax.add_patch(FancyBboxPatch((x - LEAF_W / 2, LEAF_Y), LEAF_W, LEAF_W, boxstyle="round,pad=0,rounding_size=0.006",
                                facecolor=S.CLASSICAL if on else PALE_FILL,
                                edgecolor=S.CLASSICAL_DEEP if on else PALE, lw=0.6, zorder=3))
    for dy in (-0.009, 0.0, 0.009):
        ax.plot([x - 0.011, x + 0.011], [LEAF_Y + LEAF_W / 2 + dy] * 2, color="white" if on else PALE,
                lw=0.6, solid_capstyle="round", zorder=4)


def draw(ax):
    root_ports = node(ax, 0.5, 0.45, 0.24, 0.06, VISIT_ROOT)
    for i, xc in enumerate([0.13, 0.377, 0.623, 0.87]):
        hits = VISIT_INNER.get(i, set())
        link(ax, root_ports[i], (xc, 0.31), i in VISIT_ROOT)
        for k, port in enumerate(node(ax, xc, 0.25, 0.2, 0.06, hits)):
            link(ax, port, (port[0], LEAF_Y + LEAF_W), k in hits)
            leaf(ax, port[0], k in hits)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 0.54)
    ax.set_aspect("equal")
    ax.set_axis_off()


if __name__ == "__main__":
    C.export(draw, "part8_index_tree", *SIZE_MM)
    print("wrote part8_index_tree")
