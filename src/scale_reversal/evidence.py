"""Locations of the sealed evidence, read from environment variables.

``SR_EVIDENCE`` is the root of the sealed evidence archive, the same variable
the figure scripts use. Every artefact defaults to a run directory under it
and can be overridden by its own variable:

=====================  ===============================================  ==========================
variable               artefact                                         default under SR_EVIDENCE
=====================  ===============================================  ==========================
``SR_LEDGERS``         per-tree ledgers ``<host>/outputs/<source>/      ``cities_context_perturbation_20260921_v1r1/evidence``
                       <date>/<tree>.jsonl.gz``
``SR_COHORT_TABLES``   ``endpoints.csv.gz``, ``scale_pairs.csv.gz``     ``cities_context_perturbation_20260921_v1r1/tables``
``SR_COHORT_INPUTS``   ``geometry_qa.json``, ``queries/<source>.json``  ``cities_context_perturbation_20260921_v1r1/inputs``
``SR_SWEEP_TABLES``    ``price_grid.csv``, ``price_by_source.csv``,     ``cities_price_sweep_20260924_v1/tables``
                       ``price_pairs.csv``
``SR_AA_TABLES``       ``aa_endpoints.csv.gz``, ``aa_by_source.csv``    ``cities_method_monitoring_stage_20260922_v1/tables``
``SR_TASK_ARCHIVE``    archive root holding the task runs               ``SR_EVIDENCE`` itself
=====================  ===============================================  ==========================

Run labels are directory names of the sealed archive, not file-system paths.
"""
from __future__ import annotations

import os
from pathlib import Path

EVIDENCE_VARIABLE = "SR_EVIDENCE"

COHORT_RUN = "cities_context_perturbation_20260921_v1r1"
SWEEP_RUN = "cities_price_sweep_20260924_v1"
AA_RUN = "cities_method_monitoring_stage_20260922_v1"

ARTEFACTS: dict[str, tuple[str, str]] = {
    "ledgers": ("SR_LEDGERS", f"{COHORT_RUN}/evidence"),
    "cohort_tables": ("SR_COHORT_TABLES", f"{COHORT_RUN}/tables"),
    "cohort_inputs": ("SR_COHORT_INPUTS", f"{COHORT_RUN}/inputs"),
    "sweep_tables": ("SR_SWEEP_TABLES", f"{SWEEP_RUN}/tables"),
    "aa_tables": ("SR_AA_TABLES", f"{AA_RUN}/tables"),
    "task_archive": ("SR_TASK_ARCHIVE", ""),
}
"""Artefact name to (override variable, run label under ``SR_EVIDENCE``)."""


class EvidenceNotConfigured(LookupError):
    """Neither the artefact variable nor ``SR_EVIDENCE`` is set."""


def locate(artefact: str) -> Path:
    """Directory of a sealed artefact (see the table in the module docstring).

    The artefact's own variable wins; otherwise the run label is resolved
    under ``SR_EVIDENCE``. Raises :class:`EvidenceNotConfigured` when neither
    is set and :class:`NotADirectoryError` when the location does not exist.
    """
    variable, label = ARTEFACTS[artefact]
    value = os.environ.get(variable, "").strip()
    if value:
        path = Path(value).expanduser()
    else:
        root = os.environ.get(EVIDENCE_VARIABLE, "").strip()
        if not root:
            raise EvidenceNotConfigured(f"set {EVIDENCE_VARIABLE} (or {variable}); see docs/reproduction.md")
        path = Path(root).expanduser() / label
    if not path.is_dir():
        raise NotADirectoryError(f"{artefact}: {path} is not a directory")
    return path
