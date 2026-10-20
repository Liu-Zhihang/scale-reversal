"""Figure 1 parts: estimate-versus-observation glyphs (vector, no text).

part5_estimate: the estimate from the background (filled dot) joined to the
held-out observation (open dot); the bracket marks their absolute error.
part6_error_pair: the same error for the smaller window of a pair (quantum
colour) and the larger window (observation teal) against one observation
line, the comparison the reconstruction tasks score. Labels are added in the
slide or by the assembly script. Exported as editable SVG and transparent
1,000 dpi PNG.
"""
import fig1_parts_common as C
import style as S

ESTIMATE_MM = (22.0, 10.0)
PAIR_MM = (22.0, 12.0)


def limits(ax, xlim, ylim):
    """Glyph limits; the axes stretch to the canvas because markers are sized in points."""
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_axis_off()


def draw_estimate(ax):
    """Filled estimate joined to the open held-out observation, with an error bracket."""
    ax.plot([0, 1], [0, 0], color=S.INK, lw=0.9, solid_capstyle="butt", zorder=1)
    ax.plot([0, 0, 1, 1], [0.3, 0.45, 0.45, 0.3], color=S.MID_GREY, lw=0.7, solid_joinstyle="miter", zorder=1)
    ax.scatter([0], [0], s=46, color=S.INK, edgecolors="white", linewidths=0.6, zorder=2)
    ax.scatter([1], [0], s=46, color="white", edgecolors=S.INK, linewidths=1.0, zorder=2)
    limits(ax, (-0.15, 1.15), (-0.45, 0.75))


def draw_error_pair(ax):
    """Errors of the smaller (quantum colour) and larger (teal) window against one observation line."""
    ax.plot([0, 0], [-0.7, 0.7], color=S.MID_GREY, lw=0.7, ls=(0, (2.2, 1.6)), zorder=1)
    for y, x, color in [(0.32, 0.38, S.QUANTUM_DEEP), (-0.32, 0.92, S.CLASSICAL)]:
        ax.plot([0, x], [y, y], color=color, lw=1.2, solid_capstyle="butt", zorder=2)
        ax.scatter([x], [y], s=34, color=color, edgecolors="white", linewidths=0.6, zorder=3)
    ax.scatter([0, 0], [0.32, -0.32], s=22, color="white", edgecolors=S.INK, linewidths=0.9, zorder=3)
    limits(ax, (-0.12, 1.1), (-0.75, 0.75))


if __name__ == "__main__":
    C.export(draw_estimate, "part5_estimate", *ESTIMATE_MM)
    C.export(draw_error_pair, "part6_error_pair", *PAIR_MM)
    print("wrote part5_estimate, part6_error_pair")
