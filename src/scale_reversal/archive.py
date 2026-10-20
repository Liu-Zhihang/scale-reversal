"""Readers for the layout of the sealed evidence archive.

* Ledgers: ``<root>/<host>/outputs/<source_id>/<date>/<tree>.jsonl.gz``, one
  gzip JSON-lines ledger per source-day and tree kind in the row schema of
  :mod:`qrq.ledger`.
* Cohort tables: ``endpoints.csv.gz`` (one row per window and comparator,
  with the source's city in column ``city``) and ``scale_pairs.csv.gz``.
* Inputs: ``geometry_qa.json`` (reference point of every source in its
  metric CRS) and ``queries/<source_id>.json`` (registered windows with
  bounds).

The study groups its sources by city; :func:`read_groups` returns that
grouping as the group labels :mod:`qrq.sweep` expects.
"""
from __future__ import annotations

import collections
import csv
import gzip
import json
from pathlib import Path
from typing import Any, Sequence

from qrq.index import TREE_KINDS
from qrq.ledger import LedgerDay

GROUP_COLUMN = "city"
"""Column of the sealed endpoint table that holds each source's group label."""


def find_ledger_days(root: str | Path, trees: Sequence[str] = TREE_KINDS) -> list[LedgerDay]:
    """Every complete source-day of the ledger tree, sorted by host, source and date.

    Raises :class:`ValueError` when a source-day lacks one of ``trees``.
    """
    root = Path(root)
    found: dict[tuple[str, str, str], dict[str, Path]] = collections.defaultdict(dict)
    for path in sorted(root.glob("*/outputs/*/*/*.jsonl.gz")):
        tree = path.name[: -len(".jsonl.gz")]
        if tree not in trees:
            continue
        date_dir = path.parent
        host = date_dir.parent.parent.parent.name
        found[(host, date_dir.parent.name, date_dir.name)][tree] = path
    days = []
    for (_, source, date), paths in sorted(found.items()):
        missing = [t for t in trees if t not in paths]
        if missing:
            raise ValueError(f"{source} {date}: missing ledgers for {missing}")
        days.append(LedgerDay(source, date, {t: paths[t] for t in trees}))
    return days


def read_csv(path: str | Path) -> list[dict[str, str]]:
    """Rows of a plain or gzip CSV file as strings."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_groups(tables: str | Path) -> dict[str, str]:
    """Source identifier to group label (the source's city) from ``endpoints.csv.gz``."""
    return {row["source_id"]: row[GROUP_COLUMN] for row in read_csv(Path(tables) / "endpoints.csv.gz")}


def read_reference_points(inputs: str | Path) -> dict[str, tuple[float, float]]:
    """Source identifier to reference point ``(x, y)`` from ``geometry_qa.json``."""
    sources = json.loads((Path(inputs) / "geometry_qa.json").read_text(encoding="utf-8"))
    return {s["source_id"]: (s["reference"]["x"], s["reference"]["y"]) for s in sources}


def read_registered_queries(inputs: str | Path, source_id: str) -> list[dict[str, Any]]:
    """Registered queries of one source from ``queries/<source_id>.json``."""
    return json.loads((Path(inputs) / "queries" / f"{source_id}.json").read_text(encoding="utf-8"))
