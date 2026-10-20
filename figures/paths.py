"""Locations of figure inputs and outputs, all read from environment variables.

Nothing is hard-coded; see README.md for the full description.

SR_FIGURE_DATA   figure source tables (CSV/JSON tables, density grids and the
                 basemap layers in basemap/). Required by every data figure.
SR_EVIDENCE      root of the sealed evidence archive. The source tables are
                 built from it, and a few figures read sealed tables directly.
SR_FIGURE_OUT    output directory, default ./figure_output (relative to the
                 working directory). Figure 1 parts go to figure1_parts/ and
                 audit reports to qa/ inside it.
SR_TILE_CACHE    basemap tile cache, default ~/.cache/scale_reversal_tiles.
SR_FIGURE_AUDIT  optional directory holding the figure audit helpers
                 (audit_panel_alignment.py, audit_pdf_text.py and
                 audit_figure_collisions.py). When unset, the panel-alignment
                 gate and the font and collision audits are skipped and one
                 notice says so.

Data locations resolve on first use, so the purely schematic Figure 1 parts
can be drawn without any data.
"""
import os
from pathlib import Path

# Set once the skipped-audit notice has been printed, so that make_all.py and the
# scripts it starts print it only once per run.
_NOTICE_FLAG = "SR_FIGURE_AUDIT_NOTICE_SHOWN"


def _from_env(name, default=None):
    """Path from environment variable `name`, else `default`; a required location without a value stops the run."""
    value = os.environ.get(name, "").strip()
    if value:
        return Path(value).expanduser()
    if default is None:
        raise SystemExit(f"{name} is not set; see figures/README.md for the locations the figures need")
    return Path(default).expanduser()


def figure_data():
    return _from_env("SR_FIGURE_DATA")


def evidence():
    return _from_env("SR_EVIDENCE")


def figure_out():
    return _from_env("SR_FIGURE_OUT", "figure_output")


def figure1_parts():
    return figure_out() / "figure1_parts"


def qa():
    return figure_out() / "qa"


def tile_cache():
    return _from_env("SR_TILE_CACHE", "~/.cache/scale_reversal_tiles")


def audit_tools():
    """Directory of the optional audit helpers, or None when SR_FIGURE_AUDIT is unset."""
    value = os.environ.get("SR_FIGURE_AUDIT", "").strip()
    return Path(value).expanduser() if value else None


def audit_notice_once():
    """Print the skipped-audit notice unless this run has already printed it."""
    if os.environ.get(_NOTICE_FLAG):
        return
    print("SR_FIGURE_AUDIT is not set: panel-alignment, font-size and collision audits are skipped.", flush=True)
    os.environ[_NOTICE_FLAG] = "1"
