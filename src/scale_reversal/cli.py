"""Command line: reproduce the published numbers from the sealed evidence.

::

    python -m scale_reversal cohort      # cohort totals and per-source table
    python -m scale_reversal sweep       # 45-point price sweep, four report points
    python -m scale_reversal amplified   # amplitude-amplification sensitivity
    python -m scale_reversal tasks       # reconstruction-task comparison
    python -m scale_reversal all         # everything above

Locations come from ``SR_EVIDENCE`` and its overrides
(:mod:`scale_reversal.evidence`). ``--out DIR`` writes the reproduced tables
as CSV in the layout of the sealed tables; ``--check`` compares the
reproduced numbers with the published ones and exits with status 1 on any
difference. The ``tasks`` command needs pandas.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import fields
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from qrq.ledger import LedgerCohort, LedgerEndpoint

from . import amplified, cohort, price_sweep, task_inputs, tasks
from .archive import read_groups
from .evidence import locate

Report = dict[str, Any]


CSV_MODULE = "\r\n"
TABLE_LIBRARY = "\n"
"""Line endings of the sealed tables: the sweep tables were written with the
csv module, the AA and task tables with a table library."""


def write_csv(path: Path, rows: Iterable[Mapping[str, Any]], line_end: str = CSV_MODULE) -> None:
    """Write rows as CSV; ``None`` and ``nan`` become empty cells."""
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [], lineterminator=line_end)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if v is None or (isinstance(v, float) and math.isnan(v)) else v
                             for k, v in row.items()})


class Session:
    """Lazily computed cohorts shared by the commands of one run."""

    def __init__(self) -> None:
        self._cohorts: dict[bool, LedgerCohort] = {}
        self._groups: dict[str, str] | None = None

    def cohort(self, amplified_route: bool = False) -> LedgerCohort:
        if amplified_route not in self._cohorts:
            self._cohorts[amplified_route] = cohort.reproduce(locate("ledgers"), amplified=amplified_route)
        return self._cohorts[amplified_route]

    def groups(self) -> dict[str, str]:
        if self._groups is None:
            self._groups = read_groups(locate("cohort_tables"))
        return self._groups


def _differences(got: Mapping[str, Any], expected: Mapping[str, Any]) -> list[str]:
    return [f"{k}: {got.get(k)!r} != {v!r}" for k, v in expected.items() if got.get(k) != v]


def run_cohort(session: Session, out: Path | None) -> tuple[Report, list[str]]:
    result = session.cohort()
    summary = result.summary()
    problems = _differences(summary, cohort.PUBLISHED)
    for source, values in cohort.PUBLISHED_BY_SOURCE.items():
        got = summary["by_source"].get(source, {})
        row = (got.get("windows"), got.get("quantum_lower"), got.get("forward"), got.get("reverse"))
        if row != values:
            problems.append(f"{source}: {row} != {values}")
    if out is not None:
        columns = [f.name for f in fields(LedgerEndpoint) if f.name != "trees"]
        write_csv(out / "cohort_windows.csv", ({c: getattr(w, c) for c in columns} for w in result.windows))
        write_csv(out / "cohort_pairs.csv", (vars(p) for p in result.pairs))
    return summary, problems


def run_sweep(session: Session, out: Path | None) -> tuple[Report, list[str]]:
    tables = price_sweep.price_tables(session.cohort(), session.groups())
    rows = {(r["lookup"], r["quantum_geometry"]): r for r in tables.grid}
    report: Report = {"points": len(rows), "report_points": {}}
    problems = []
    for point, expected in price_sweep.REPORTED.items():
        r = rows[point]
        got = (r["lower_windows"], round(r["q_over_c_median"], 2), r["forward_pairs"], r["reverse_pairs"])
        report["report_points"][f"{point[0]}/{point[1]}"] = dict(zip(
            ("lower_windows", "q_over_c_median", "forward_pairs", "reverse_pairs"), got))
        if got != expected:
            problems.append(f"{point}: {got} != {expected}")
    unit = rows[(1, 1)]
    report["unit_transitions"] = [unit["forward_retained"], unit["forward_added"], unit["forward_lost"]]
    if report["unit_transitions"] != [907, 450, 153]:
        problems.append(f"unit transitions {report['unit_transitions']} != [907, 450, 153]")
    if out is not None:
        write_csv(out / "price_grid.csv", tables.grid)
        write_csv(out / "price_by_source.csv", tables.by_source)
        write_csv(out / "price_pairs.csv", tables.pairs)
    return report, problems


def run_amplified(session: Session, out: Path | None) -> tuple[Report, list[str]]:
    legacy, joint = session.cohort(), session.cohort(amplified_route=True)
    report = amplified.sensitivity(legacy, joint, session.groups())
    problems = _differences(report, amplified.PUBLISHED_AA)
    groups = (report["groups_with_forward"], report["groups"])
    if groups != amplified.PUBLISHED_AA_GROUPS:
        problems.append(f"groups {groups} != {amplified.PUBLISHED_AA_GROUPS}")
    if out is not None:
        write_csv(out / "aa_by_source.csv", amplified.aa_by_source(legacy, joint), TABLE_LIBRARY)
    return report, problems


def family_readouts(row: Mapping[str, Any]) -> Report:
    """Published rounding of one family row of the task comparison."""
    decimals = 4 if row["family"] == "speed" else 3
    return dict(
        sources=row["sources"], source_days=row["source_days"], forward_n=row["forward_n"],
        forward_pct=round(100 * row["forward_worse_rate"], 2),
        control_pct=round(100 * row["standardised_control_worse_rate"], 2),
        delta_pp=round(100 * row["delta"], decimals),
        interval_pp=(round(100 * row["delta_ci_low"], 3), round(100 * row["delta_ci_high"], 3)),
    )


def run_tasks(session: Session, out: Path | None) -> tuple[Report, list[str]]:
    pairs, registry = task_inputs.load_task_inputs(locate("task_archive"))
    result = tasks.compare_crossings(pairs, registry, task_inputs.FAMILY_ORDER)
    report: Report = {}
    problems: list[str] = []
    for row in result.family_rows():
        report[row["family"]] = family_readouts(row)
        problems += [f"{row['family']} {p}" for p in
                     _differences(report[row["family"]], task_inputs.PUBLISHED_FAMILIES[row["family"]])]
    if out is not None:
        write_csv(out / "family_summary.csv", result.family_rows(), TABLE_LIBRARY)
        write_csv(out / "by_task_source.csv", result.source_rows(), TABLE_LIBRARY)
        write_csv(out / "strata.csv", result.stratum_rows(), TABLE_LIBRARY)
        write_csv(out / "category_summary.csv", tasks.category_summary(pairs), TABLE_LIBRARY)
    return report, problems


COMMANDS: dict[str, Callable[[Session, Path | None], tuple[Report, list[str]]]] = {
    "cohort": run_cohort,
    "sweep": run_sweep,
    "amplified": run_amplified,
    "tasks": run_tasks,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="scale-reversal", description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=[*COMMANDS, "all"])
    parser.add_argument("--out", type=Path, help="write the reproduced tables as CSV to this directory")
    parser.add_argument("--check", action="store_true", help="exit with status 1 if a published number differs")
    args = parser.parse_args(argv)
    session = Session()
    names = list(COMMANDS) if args.command == "all" else [args.command]
    reports, problems = {}, []
    for name in names:
        reports[name], found = COMMANDS[name](session, args.out)
        problems += [f"{name}: {p}" for p in found]
    reports["differences_from_published"] = problems
    print(json.dumps(reports, indent=2, default=str))
    return 1 if args.check and problems else 0
