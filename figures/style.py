"""Shared style and export for the manuscript figures.

Visual conventions follow Nature-family figures: sans-serif type, open axes and
direct labels, with a magma (orange to purple) and deep-teal palette in which
magma tones always mark lower quantum-filtering cost and teal marks
classical-led preparation or other pairs. Panel letters are bold and bracketed, (a), as is usual in Elsevier
journals. Export follows the Elsevier artwork rules for
Cities: 190 mm full-page width, line art as PNG at 1,000 dpi (at least 7,480 px
wide) and no figure title inside the artwork, because the title belongs to the
caption.

Only PNG is written to the output directory (SR_FIGURE_OUT). The PDF needed for
the font-size and collision audits is rendered into a temporary directory and
discarded; the audit reports are kept as JSON in SR_FIGURE_OUT/qa. The
alignment gate and both audits run only when SR_FIGURE_AUDIT points to the
audit helpers (see paths.py).
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import time

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.transforms import ScaledTranslation  # noqa: E402
from PIL import Image  # noqa: E402

import paths as P  # noqa: E402

OUT = P.figure_out()
QA = P.qa()
AUDIT_TOOLS = P.audit_tools()


def __getattr__(name):
    """Data locations (S.SOURCE, S.EVIDENCE) resolve on first use, so data-free parts need no data."""
    if name == "SOURCE":
        return P.figure_data()
    if name == "EVIDENCE":
        return P.evidence()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ---- Elsevier artwork contract -------------------------------------------
MM = 1 / 25.4
FULL_WIDTH_MM = 190
LINE_ART_DPI = 1000
MIN_FULL_WIDTH_PX = 7480
MIN_TEXT_PT = 6.0

# ---- Palette: magma (orange to purple) for quantum, deep teal for classical --
QUANTUM = "#F4675C"        # markers: lower quantum-filtering cost, forward reversal
QUANTUM_DEEP = "#B5367A"   # magenta text and outlines in the quantum family
CLASSICAL = "#1F6F78"      # deep teal: classical-led preparation, other pairs
CLASSICAL_MID = "#3F8389"
CLASSICAL_DEEP = "#134A50"
URBAN = "#7E9C84"          # sage: urban analysis layer
RISK = "#C8462D"           # vermilion: risk annotations
INK = "#2B2F33"
GREY = "#6E7377"
MID_GREY = "#A9ADB0"
LIGHT_GREY = "#DCDDDB"
PALE_WARM = "#FFF4EC"

# Light palette for secondary panels and supplementary figures: same meanings,
# lower saturation, with deeper partners for text and outlines.
SOFT_WARM, SOFT_WARM_TEXT = "#EFA48C", "#B4553A"            # quantum cheaper, worse error
SOFT_TERRACOTTA = "#E3A3A8"
SOFT_CLASSICAL, SOFT_CLASSICAL_TEXT = "#8FBFC2", "#1F5F66"  # classical cheaper, better error
PALE_CLASSICAL = "#D6E6E6"
SAND = "#EBDCC5"                                             # empty windows
STONE = "#CFCAC3"                                            # unchanged or neutral

WARM_SEQ = LinearSegmentedColormap.from_list(
    "warm_seq", ["#FEF7DC", "#FEC287", "#FB8861", "#E0455F", "#A8327D", "#6A1C81"])
WARM_STRONG = LinearSegmentedColormap.from_list(
    "warm_strong", ["#FEC287", "#F4675C", "#C83B74", "#7A2181"])
CLASSICAL_SEQ = LinearSegmentedColormap.from_list(
    "classical_seq", ["#EEF4F4", "#C2DADB", "#86B4B7", "#3F8389", "#1F6F78", "#123F45"])
# Diverging about Q = C: warm below parity (quantum cheaper), teal above. The
# centre is deliberately not white, so points near parity stay visible.
DIVERGING = LinearSegmentedColormap.from_list(
    "diverging", ["#A8327D", "#F4675C", "#FDB57A", "#A9CDCF", "#3F8389", "#123F45"])

SOURCE_LABEL = {
    "tdrive": "Beijing T-Drive", "geolife": "Beijing GeoLife", "jinan": "Jinan",
    "dublin": "Dublin", "porto": "Porto", "montreal": "Montréal",
    "barcelona": "Barcelona", "rio": "Rio de Janeiro", "stellenbosch": "Stellenbosch",
    "nyc_mat": "New York City (MAT)", "paris_mat": "Paris (MAT)",
    "sf_cabspotting": "San Francisco", "rome_taxi": "Rome", "brighton_shl": "Brighton (SHL)",
}
SOURCE_CITY = {k: ("Beijing" if k in ("tdrive", "geolife") else v.split(" (")[0])
               for k, v in SOURCE_LABEL.items()}


def apply():
    """Set the shared rcParams; call once before creating a figure."""
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"],
        "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7,
        "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
        "axes.linewidth": 0.6, "axes.edgecolor": INK, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.major.pad": 2, "ytick.major.pad": 2, "axes.labelpad": 3,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "legend.handletextpad": 0.4,
        "pdf.fonttype": 42, "svg.fonttype": "none", "mathtext.default": "regular",
        "savefig.facecolor": "white", "figure.facecolor": "white",
    })


def panel_label(ax, letter, dx_pt=-24, dy_pt=5):
    """Bold bracketed panel letter, (a), just outside the top-left plot corner."""
    offset = ScaledTranslation(dx_pt / 72, dy_pt / 72, ax.figure.dpi_scale_trans)
    ax.text(0, 1, f"({letter})", transform=ax.transAxes + offset, ha="left", va="bottom",
            fontsize=10, fontweight="bold", color=INK)


def stacked_keys(fig, ax, mappables, labels, ticks, ticklabels, frac=0.36):
    """Thin horizontal colour keys stacked above the top-right of an axes.

    Only the top key carries tick labels, so every key must share one norm.
    """
    fig.canvas.draw()
    pos = ax.get_position()
    fh = fig.get_figheight()
    h, gap, base = 1.3 * MM / fh, 1.3 * MM / fh, 2.4 * MM / fh
    axes = []
    for i, (mappable, label) in enumerate(zip(mappables, labels)):
        y = pos.y1 + base + (len(mappables) - 1 - i) * (h + gap)
        cax = fig.add_axes([pos.x1 - frac * pos.width, y, frac * pos.width, h])
        cb = fig.colorbar(mappable, cax=cax, orientation="horizontal", ticks=ticks)
        cb.outline.set_linewidth(0.4)
        cax.xaxis.set_minor_locator(mpl.ticker.NullLocator())
        top = i == 0
        cax.tick_params(labelsize=6.2, length=1.5 if top else 0, width=0.4, pad=1, top=top,
                        bottom=False, labeltop=top, labelbottom=False)
        if top:
            cb.set_ticklabels(ticklabels)
        cax.text(-0.04, 0.5, label, transform=cax.transAxes, ha="right", va="center", fontsize=6.3)
        axes.append(cax)
    return axes


def log2_ratio_ticks(ax, axis, exponents):
    """Label a log2(Q/C) axis with the ratios themselves (1/8, 1, 8, ...)."""
    labels = [f"1/{2 ** -e:,}" if e < 0 else f"{2 ** e:,}" for e in exponents]
    (ax.set_xticks if axis == "x" else ax.set_yticks)(exponents, labels)


def _panel_alignment_gate():
    """The alignment gate from the optional audit helpers in SR_FIGURE_AUDIT."""
    if str(AUDIT_TOOLS) not in sys.path:
        sys.path.insert(0, str(AUDIT_TOOLS))
    from audit_panel_alignment import require_matplotlib_panel_alignment
    return require_matplotlib_panel_alignment


def save(fig, name, exclude_axes=(), full_width=True, accepted_overlaps=None, schematic=False, **align_kwargs):
    """Alignment gate, 1,000 dpi PNG export, then font and collision audits.

    accepted_overlaps maps a text string to the reason its collision findings are
    intentional (for example map labels over borders); those findings are kept
    in the collision report with the reason, and only the rest can block export.

    The gate and the audits need SR_FIGURE_AUDIT. Without it the PNG is still
    written and its width checked, and one notice says the audits were skipped.
    """
    fig.canvas.draw()
    OUT.mkdir(parents=True, exist_ok=True)
    audited = AUDIT_TOOLS is not None
    if not audited:
        P.audit_notice_once()
    elif schematic:
        # A single-canvas schematic has no comparable data panels to align.
        QA.mkdir(parents=True, exist_ok=True)
        (QA / f"{name}.alignment.json").write_text(json.dumps(
            {"status": "NOT APPLICABLE", "reason": "single-canvas schematic without comparable data panels"}, indent=1))
    else:
        QA.mkdir(parents=True, exist_ok=True)
        _panel_alignment_gate()(
            fig, json_out=str(QA / f"{name}.alignment.json"), exclude_axes=list(exclude_axes),
            tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True, **align_kwargs)
    png = OUT / f"{name}.png"
    # Render to a local temporary file first: a synced or network output folder
    # can briefly lock a PNG that is open in a viewer, which fails a direct write.
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / png.name
        fig.savefig(staged, dpi=LINE_ART_DPI)
        for attempt in range(6):
            try:
                shutil.copyfile(staged, png)
                break
            except OSError:
                if attempt == 5:
                    raise
                time.sleep(2)
    if audited:
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / f"{name}.pdf"
            fig.savefig(pdf)
            fonts = subprocess.run(
                [sys.executable, str(AUDIT_TOOLS / "audit_pdf_text.py"), "--min-pt", str(MIN_TEXT_PT),
                 "--json", str(pdf)], capture_output=True, text=True)
            (QA / f"{name}.fonts.json").write_text(fonts.stdout)
            collisions = subprocess.run(
                [sys.executable, str(AUDIT_TOOLS / "audit_figure_collisions.py"), str(pdf),
                 "--json-out", str(QA / f"{name}.collisions.json")], capture_output=True, text=True)
    plt.close(fig)
    width_px, height_px = Image.open(png).size
    if full_width and width_px < MIN_FULL_WIDTH_PX:
        raise SystemExit(f"{name}: {width_px} px is below the Elsevier full-page minimum")
    summary = {"png": png.name, "pixels": [width_px, height_px], "dpi": LINE_ART_DPI}
    if not audited:
        summary["audits"] = "skipped"
        print(json.dumps(summary, ensure_ascii=False, indent=1))
        return summary
    summary.update({
        "font_audit_exit": fonts.returncode, "collision_audit_exit": collisions.returncode,
        "collision_summary": collisions.stdout.strip().splitlines()[-3:],
    })
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    blocking = collisions.returncode == 1
    if blocking and accepted_overlaps:
        report_path = QA / f"{name}.collisions.json"
        report = json.loads(report_path.read_text())
        findings = report.get("findings", [])
        for f in findings:
            if f.get("text") in accepted_overlaps:
                f["accepted_reason"] = accepted_overlaps[f["text"]]
        remaining = [f for f in findings if f.get("severity") == "FAIL" and "accepted_reason" not in f]
        report["accepted_overlap_count"] = sum("accepted_reason" in f for f in findings)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1))
        blocking = bool(remaining)
        summary["unaccepted_fail"] = [f["text"] for f in remaining]
        print("accepted overlaps:", report["accepted_overlap_count"], "unaccepted FAIL:", summary["unaccepted_fail"])
    if fonts.returncode or blocking:
        print(fonts.stdout[-1500:], collisions.stdout[-3000:], sep="\n")
        raise SystemExit(f"{name}: audit failed")
    return summary
