"""Build the figure source tables (optional), then render every figure and Figure 1 part.

Dependency order:
1. with --build-tables: build_tables_statistics.py and build_tables_geography.py
   write the source tables from SR_EVIDENCE into SR_FIGURE_DATA;
2. the twelve Figure 1 parts (ten modules), then fig1_assemble.py, which places
   the same drawings on the 190 mm canvas;
3. Figures 2-6 and Supplementary Figures S1-S3.

Each script runs in its own Python process, exactly as when run by hand, so no
plotting state carries over from one figure to the next. The run stops at the
first failure. fetch_rome_layers.py is not run here: it needs network access
and the restricted Rome point records, and it only refreshes inputs of step 2.
"""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import time

import paths as P

HERE = Path(__file__).resolve().parent
TABLES = ["build_tables_statistics", "build_tables_geography"]
PARTS = ["fig1_part_world", "fig1_part_city", "fig1_part_cube", "fig1_part_background", "fig1_part_estimate",
         "fig1_part_windows", "fig1_part_index", "fig1_part_routes", "fig1_part_reversal", "fig1_part_checklist"]
FIGURES = ["fig1_assemble", "fig2_geography", "fig3_reversal", "fig4_prices", "fig5_boundary", "fig6_tasks",
           "figS1_cities", "figS2_same_answer", "figS3_monitoring"]


def resolved_env():
    """Environment for the scripts with every location made absolute, so all of them agree."""
    env = dict(os.environ)
    env["SR_FIGURE_OUT"] = str(P.figure_out().resolve())
    env["SR_TILE_CACHE"] = str(P.tile_cache().resolve())
    for name in ("SR_FIGURE_DATA", "SR_EVIDENCE", "SR_FIGURE_AUDIT"):
        if env.get(name, "").strip():
            env[name] = str(Path(env[name].strip()).expanduser().resolve())
    return env


def run(script, env):
    start = time.time()
    print(f"==> {script}.py", flush=True)
    done = subprocess.run([sys.executable, str(HERE / f"{script}.py")], env=env)
    if done.returncode:
        raise SystemExit(f"{script}.py failed with exit code {done.returncode}")
    print(f"    {script}.py finished in {time.time() - start:.0f} s", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--build-tables", action="store_true",
                        help="rebuild the source tables from SR_EVIDENCE into SR_FIGURE_DATA before rendering")
    parser.add_argument("--tables-only", action="store_true", help="rebuild the source tables and stop")
    parser.add_argument("--only", nargs="+", metavar="SCRIPT",
                        help="render only these scripts (names without .py), kept in dependency order")
    args = parser.parse_args(argv)
    render = PARTS + FIGURES
    if args.only:
        unknown = sorted(set(args.only) - set(render))
        if unknown:
            parser.error(f"unknown scripts: {', '.join(unknown)}; choose from {', '.join(render)}")
        render = [s for s in render if s in args.only]
    if P.audit_tools() is None:
        P.audit_notice_once()
    env = resolved_env()
    steps = (TABLES if args.build_tables or args.tables_only else []) + ([] if args.tables_only else render)
    for script in steps:
        run(script, env)
    if not args.tables_only:
        print("outputs in", env["SR_FIGURE_OUT"])


if __name__ == "__main__":
    main()
