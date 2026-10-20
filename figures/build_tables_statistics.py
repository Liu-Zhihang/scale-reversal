"""Source tables for Figures 3-6, copied from the sealed evidence archive.

Run from any directory. No sampling, trees, server access or writes to the
archive. All scientific source tables are copied as derived views with input
hashes. The figures themselves are drawn by the fig*.py scripts in this folder
from these tables.

Table names keep their historical numerical prefixes: figure2_* feed Figure 3,
figure3_* Figure 4, figure4_* Figure 5 and figure5_* Figure 6.

Reads SR_EVIDENCE. Writes the tables to SR_FIGURE_DATA (or --out) and the input
hashes to <out>/provenance/provenance.json.
"""
from pathlib import Path
import argparse
import hashlib
import json

import pandas as pd

import paths as P

SOURCE_ORDER = ['tdrive', 'geolife', 'jinan', 'dublin', 'porto', 'montreal', 'barcelona', 'rio',
                'stellenbosch', 'nyc_mat', 'paris_mat', 'sf_cabspotting', 'rome_taxi', 'brighton_shl']
# Artifact-manifest digests of the two packages admitted by the package review
# (decision PASS_ADMIT_B10_B11_TO_E5r3). No table is written if either package
# differs from the admitted state.
ADMITTED_MANIFEST_SHA256 = {
    'cities_price_sweep_20260924_v1': 'a32d85407f851dcca544d8e98398e52cb7c3f0f48eca68a1dff07005eea90728',
    'cities_crossing_information_20260924_v1': 'a11374396ac28217318180d1c849ca05af8d252068842e70bcd2f2c3c364e5b2',
}
EVIDENCE = P.evidence()
SRC = None   # output directory for the tables, set in main()
provenance = {}


def read(pkg, rel):
    """Read a sealed table and record its SHA-256 under its archive-relative path."""
    p = EVIDENCE / pkg / rel
    provenance[str(p.relative_to(EVIDENCE))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return pd.read_csv(p)


def source(df, name):
    df.to_csv(SRC / name, index=False)


def load():
    ep = read('cities_context_perturbation_20260921_v1r1', 'tables/endpoints.csv.gz')
    ep = ep[ep.comparator.eq('envelope') & ep.arm.eq('baseline') & ep.variant.eq('base')].copy()
    ep['lower'] = ep.Q < ep.C
    pairs = read('cities_context_perturbation_20260921_v1r1', 'tables/scale_pairs.csv.gz')
    pairs = pairs[pairs.comparator.eq('envelope') & pairs.arm.eq('baseline') & pairs.variant.eq('base')].copy()
    assert len(ep) == 13370 and ep.lower.sum() == 742
    assert len(pairs) == 17592 and pairs.direction.eq('forward').sum() == 1060
    return ep, pairs


def fig3_tables(ep, pairs):
    grid = ep.groupby(['duration_s', 'width_m']).agg(n=('lower', 'size'), lower=('lower', 'sum')).reset_index()
    source(grid, 'figure2_extent_grid.csv')
    source(pairs[['source_id', 'date', 'small_query', 'large_query', 'small_D', 'large_D', 'direction']],
           'figure2_pairs.csv.gz')
    counts = pairs.groupby('source_id').agg(
        n=('direction', 'size'), forward=('direction', lambda v: v.eq('forward').sum()),
        reverse=('direction', lambda v: v.eq('reverse').sum())).reindex(SOURCE_ORDER).reset_index()
    source(counts, 'figure2_sources.csv')


def fig4_tables():
    grid = read('cities_price_sweep_20260924_v1', 'tables/price_grid.csv')
    src = read('cities_price_sweep_20260924_v1', 'tables/price_pairs.csv')
    src = src[src.axis.eq('all') & ~src.source_id.eq('ALL')].copy()
    source(grid, 'figure3_prices.csv')
    source(src, 'figure3_sources.csv')


def fig5_tables(ep):
    # Strictly positive values are required; no pseudocount or silent filtering.
    assert (ep.k > 0).all() and (ep.M > 0).all() and (ep.trial_cost > 0).all()
    ring = read('cities_support_adjusted_geography_20260923_v1', 'runs/20260923T150413Z/ring_pooled.csv')
    source(ep[['source_id', 'date', 'query_id', 'k', 'M', 'trial_cost', 'prefix', 'Q', 'C', 'c_route']],
           'figure4_phase.csv.gz')
    source(ring, 'figure4_geography.csv')


def fig6_tables():
    src = read('cities_crossing_information_20260924_v1', 'tables/by_task_source.csv')
    fam = read('cities_crossing_information_20260924_v1', 'tables/family_summary.csv')
    source(src, 'figure5_sources.csv')
    source(fam, 'figure5_families.csv')


def main(argv=None):
    global SRC
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, help='output directory for the tables (default: SR_FIGURE_DATA)')
    args = parser.parse_args(argv)
    SRC = args.out.expanduser() if args.out else P.figure_data()
    SRC.mkdir(parents=True, exist_ok=True)
    for package, expected in ADMITTED_MANIFEST_SHA256.items():
        actual = hashlib.sha256((EVIDENCE / package / 'artifact_manifest.json').read_bytes()).hexdigest()
        assert actual == expected, f'{package}: artifact manifest differs from the admitted package'
    ep, pairs = load()
    fig3_tables(ep, pairs)
    fig4_tables()
    fig5_tables(ep)
    fig6_tables()
    record = SRC / 'provenance' / 'provenance.json'
    record.parent.mkdir(exist_ok=True)
    record.write_text(json.dumps({
        'backend': 'Python/matplotlib', 'width_mm': 190, 'png_dpi': 1000,
        'drawn_by': {'figure3': 'figures/fig3_reversal.py', 'figure4': 'figures/fig4_prices.py',
                     'figure5': 'figures/fig5_boundary.py', 'figure6': 'figures/fig6_tasks.py'},
        'all_observations_retained': True, 'input_sha256': provenance}, ensure_ascii=False, indent=2) + '\n')
    print('tables for Figures 3-6 written to', SRC)


if __name__ == '__main__':
    main()
