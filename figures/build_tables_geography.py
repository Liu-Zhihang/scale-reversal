"""Source tables for the Figure 1 design numbers, Figure 2 and Supplementary Fig. S1.

Reads only released count grids and frozen M1/B09 aggregates from the sealed
evidence archive (SR_EVIDENCE). No raw coordinates or entity identifiers are
read, nothing is written to the archive and no remote access is used.

Writes to SR_FIGURE_DATA (or --out):
- figure2_anchor_counts.csv: windows with Q < C among the nonempty, fully
  supported windows of every source and registered anchor, checked against
  the B09 ring totals;
- density_grids/<source>.json: the released count grids of one grid release;
- figure1_design.json: the design numbers of the cohort and the query grid;
and the input hashes and grid summary to <out>/provenance/.

Grid releases (--grid-release):
- v1: a cell is shown only if at least five dataset-defined entities were seen
  in it on one registered day;
- v2 (default; author decision of 2026-10-20, used by the current figures): the
  entity threshold is removed and every nonempty cell shows its pooled count.
  Cell sizes, extents and source-days are those of v1, and every cell shown
  in v1 must reappear in v2 with an identical count.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json

import pandas as pd

import paths as P

ORDER = ['tdrive', 'geolife', 'jinan', 'dublin', 'porto', 'montreal', 'barcelona', 'rio', 'stellenbosch',
         'nyc_mat', 'paris_mat', 'sf_cabspotting', 'rome_taxi', 'brighton_shl']
EVIDENCE = P.evidence()
M1 = EVIDENCE / 'cities_context_perturbation_20260921_v1r1'
GRID_RELEASES = {'v1': 'cities_observation_geography_20260924_v1', 'v2': 'cities_observation_geography_20261020_v2'}
PRIVACY = {
    'v1': 'dataset-defined entity gate is not a claim of person-level anonymity; cells require >=5 on at least one day',
    'v2': 'author decision 2026-10-20: entity threshold of v1 removed; every nonempty cell shows its pooled count',
}
SRC = None   # output directory for the tables, set in main()
provenance = {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tracked(p):
    """Record the SHA-256 of a sealed input under its archive-relative path."""
    provenance[str(p.relative_to(EVIDENCE))] = sha(p)
    return p


def read(p):
    return json.loads(tracked(p).read_text())


def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False))


def read_grids(release):
    """Grid rows of one release and the closing resource record of each of its two runs.

    The grids were counted in two runs, one per compute machine; each run log
    ends with a COMPLETE record, and together they must cover every source.
    """
    grids, resources = {}, []
    run_logs = sorted((EVIDENCE / GRID_RELEASES[release] / 'runs').glob('*/grids.jsonl'))
    assert len(run_logs) == 2, run_logs
    for log in run_logs:
        p = tracked(log)
        allrows = [json.loads(line) for line in p.read_text().splitlines()]
        assert allrows[-1]['status'] == 'COMPLETE'
        resources.append(allrows[-1])
        for r in allrows:
            if r['kind'] == 'grid':
                grids[r['source_id']] = r
    return grids, resources


def load(release):
    cases = read(M1 / 'inputs/cases.json')
    geoms = read(M1 / 'inputs/geometry_qa.json')
    ep = pd.read_csv(tracked(M1 / 'tables/endpoints.csv.gz'), dtype={'anchor': str})
    ep = ep[ep.comparator.eq('envelope') & ep.arm.eq('baseline') & ep.variant.eq('base')].copy()
    ep['lower'] = ep.Q < ep.C
    assert len(ep) == 13370 and ep.lower.sum() == 742
    rows = []
    for sid in ORDER:
        for ix, iy in itertools.product(range(3), repeat=2):
            anchor = f'{ix}{iy}'
            v = ep[ep.source_id.eq(sid) & ep.anchor.eq(anchor)]
            rows.append(dict(source_id=sid, anchor=anchor, ix=ix, iy=iy, x_offset_km=(ix - 1) * 20 / 3,
                             y_offset_km=(iy - 1) * 20 / 3, lower=int(v.lower.sum()), nonempty_supported=len(v),
                             fraction=float(v.lower.mean()) if len(v) else None,
                             ring='center' if anchor == '11' else 'side' if '1' in anchor else 'corner'))
    anchors = pd.DataFrame(rows)
    b09 = pd.read_csv(tracked(EVIDENCE / 'cities_support_adjusted_geography_20260923_v1/runs/20260923T150413Z/ring_pooled.csv'))
    for r in b09.itertuples():
        v = anchors[anchors.ring.eq(r.ring)]
        assert v.lower.sum() == r.favorable and v.nonempty_supported.sum() == r.nonempty
    anchors.to_csv(SRC / 'figure2_anchor_counts.csv', index=False)

    # v1 grids: always read and checked, because v2 is defined relative to them.
    v1, v1_resources = read_grids('v1')
    assert set(v1) == set(ORDER) and len(cases) == 107 and sum(c['n'] for c in cases) == 101240625
    for sid, g in v1.items():
        assert g['registered_points'] == sum(c['n'] for c in cases if c['source_id'] == sid)
        assert g['registered_days'] == len([c for c in cases if c['source_id'] == sid])
        assert all(v is None or v >= 5 for v in g['counts'])
    assert v1['brighton_shl']['visible_cells'] == 0 and v1['dublin']['visible_cells'] == 0
    if release == 'v1':
        grids, resources = v1, v1_resources
    else:
        grids, resources = read_grids('v2')
        assert set(grids) == set(ORDER)
        for sid, g in grids.items():
            old = v1[sid]
            assert all(g[k] == old[k] for k in ('registered_points', 'registered_days', 'epsg', 'origin_xy',
                                                 'cell_m', 'shape'))
            assert all(v is None or v >= 1 for v in g['counts'])
            assert all(a is None or a == b for a, b in zip(old['counts'], g['counts']))
    for sid, g in grids.items():
        dump(SRC / 'density_grids' / f'{sid}.json', g)
    dump(SRC / 'provenance' / 'grid_summary.json', {
        'resources': resources, 'days': 107, 'points': 101240625, 'anchor_lower': 742,
        'anchor_denominator': 13370, 'ring_check': 'PASS_B09_ALL_THREE_RINGS', 'sources': [
            {k: g[k] for k in ('source_id', 'registered_days', 'registered_points', 'cell_m', 'visible_cells',
                               'entity_semantics')} for g in grids.values()]})
    return cases, {g['source_id']: g for g in geoms}, anchors, grids


def design(cases):
    """Design numbers of the cohort and the registered query grid."""
    cfg = read(M1 / 'config.json')
    tasks = pd.read_csv(tracked(EVIDENCE / 'cities_crossing_information_20260924_v1/tables/by_task_source.csv'))
    monitors = tasks[tasks.family.eq('monitoring')].source.nunique()
    speeds = tasks[tasks.family.eq('speed')].source.nunique()
    assert monitors == 4 and speeds == 9
    nums = {'sources': len(set(c['source_id'] for c in cases)), 'days': len(cases),
            'points': sum(c['n'] for c in cases), 'widths_m': cfg['widths_m'], 'durations_s': cfg['spans_s'],
            'centres_s': cfg['centers_s'], 'trees': cfg['trees'], 'requests_per_day': 6 * 4 * 9 * 3,
            'monitoring_tasks': monitors, 'speed_sources': speeds}
    dump(SRC / 'figure1_design.json', nums)


def main(argv=None):
    global SRC
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, help='output directory for the tables (default: SR_FIGURE_DATA)')
    parser.add_argument('--grid-release', choices=sorted(GRID_RELEASES), default='v2',
                        help='density-grid release to write (default: v2, used by the current figures)')
    args = parser.parse_args(argv)
    SRC = args.out.expanduser() if args.out else P.figure_data()
    SRC.mkdir(parents=True, exist_ok=True)
    cases, geom, anchors, grids = load(args.grid_release)
    design(cases)   # Figure 1 itself is drawn from the fig1_part_*.py modules by fig1_assemble.py
    dump(SRC / 'provenance' / 'supplement_provenance.json', {
        'input_files': provenance, 'script_sha256': sha(__file__),
        'scope': 'figures only; no new costs or mechanism tests',
        'output': 'source tables only; figures are drawn by the fig*.py scripts',
        'grid_release': GRID_RELEASES[args.grid_release],
        'density_transform': 'pooled count / cell area in km2; log10, positive disclosed cells only; no interpolation',
        'privacy': PRIVACY[args.grid_release]})
    print('tables for Figures 1, 2 and S1 written to', SRC, f'(grid release {args.grid_release})')


if __name__ == '__main__':
    main()
