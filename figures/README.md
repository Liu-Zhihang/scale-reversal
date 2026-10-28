# Figures

Scripts that draw every figure of the manuscript: Figures 1-6, Supplementary
Figures S1-S3 and the twelve Figure 1 parts. They also build the figure
source tables from the sealed evidence archive. The figure layer depends only
on standard scientific Python packages, not on `qrq` or `scale_reversal`.

Explained previews are in [docs/figures.md](../docs/figures.md). The
repository landing page shows Figures 1, 3, 4 and 7 with short explanations.
Figures 2, 5, 6, S2 and S3 are documented only on that page. Figure 7 is the
checklist flowchart; it is not produced by these scripts.

Figure source tables are in `evidence/figure_source`. The Rome taxi traces
used for one layer of Figure 1 are not included. Every input and output
location is read from environment variables (see `paths.py`).

## Quick start

```bash
export SR_FIGURE_DATA=/path/to/source_data     # figure source tables (required)
export SR_EVIDENCE=/path/to/evidence           # sealed evidence archive (required)
export SR_FIGURE_OUT=./figure_output           # optional, this is the default
export SR_FIGURE_AUDIT=/path/to/audit/helpers  # optional

python figures/make_all.py                     # render every figure and part
python figures/make_all.py --build-tables      # rebuild the source tables first
python figures/make_all.py --tables-only       # rebuild the source tables only
python figures/make_all.py --only fig3_reversal fig4_prices
python figures/fig3_reversal.py                # any script also runs on its own
```

`make_all.py` runs every script in its own Python process, in dependency
order: source tables (with `--build-tables`), the Figure 1 parts,
`fig1_assemble.py`, then Figures 2-6 and S1-S3. It stops at the first failure.
A full render takes about two minutes once the basemap tiles are cached.

## Environment variables

| Variable | Meaning | Default |
| --- | --- | --- |
| `SR_FIGURE_DATA` | Directory of the figure source tables (`source_data`): CSV/JSON tables, `density_grids/` and `basemap/`. | required |
| `SR_EVIDENCE` | Root of the sealed evidence archive. The table builders read it, and Figures 2, 5, S1-S3 and the Figure 1 parts read registered geometry and a few sealed tables from it directly. | required |
| `SR_FIGURE_OUT` | Output directory. Figure 1 parts go to `figure1_parts/`, audit reports to `qa/`. | `./figure_output` |
| `SR_TILE_CACHE` | Cache for the basemap tiles of Figure 2 and Supplementary Fig. S1. | `~/.cache/scale_reversal_tiles` |
| `SR_FIGURE_AUDIT` | Optional directory holding the audit helpers `audit_panel_alignment.py`, `audit_pdf_text.py` and `audit_figure_collisions.py`. When set, every figure must pass the panel-alignment gate, the 6 pt minimum font-size audit and the text-collision audit, and the reports are written to `SR_FIGURE_OUT/qa`. When unset, these checks are skipped and one notice says so. | unset |
| `SR_ROME_POINTS` | Local Rome point-record file, used only by `fetch_rome_layers.py` (or pass `--points`). | unset |

The schematic Figure 1 parts (`fig1_part_index`, `fig1_part_routes`,
`fig1_part_reversal`, `fig1_part_estimate`, `fig1_part_checklist`) need no
data; every other script needs `SR_FIGURE_DATA` and `SR_EVIDENCE`.

## Requirements

Python 3.10 or later with:

- numpy, pandas, matplotlib, Pillow
- geopandas, shapely, pyproj (map projections and clipping)
- contextily (basemap tiles for Figure 2 and Supplementary Fig. S1)
- requests (only for `fetch_rome_layers.py`)

The reference renders were made with Python 3.12, numpy 2.2, pandas 2.3,
matplotlib 3.10.8, geopandas 1.1.2, shapely 2.1.2, pyproj 3.7.2,
contextily 1.7.0 and Pillow 12.0. Text is set in Arial when installed, else
Liberation Sans. Pixel-identical output is expected only with the same fonts
and library versions. The optional audit helpers need PyMuPDF.

## Scripts and outputs

| Script | Output (in `SR_FIGURE_OUT`) |
| --- | --- |
| `fig1_part_world.py` ... `fig1_part_checklist.py` | `figure1_parts/part1_world` ... `part12_risk`, each as SVG and transparent 1,000 dpi PNG |
| `fig1_assemble.py` | `figure1_framework.png`, plus `figure1_parts/figure1_assembled.pdf` and `.svg` |
| `fig2_geography.py` | `figure2_observation_geography.png` |
| `fig3_reversal.py` | `figure3_reversal.png` |
| `fig4_prices.py` | `figure5_prices.png` |
| `fig5_boundary.py` | `figure6_boundary_geography.png` |
| `fig6_tasks.py` | `figure4_tasks.png` |
| `figS1_cities.py` | `figureS1_cities.png` |
| `figS2_same_answer.py` | `figureS2_same_answer.png` |
| `figS3_monitoring.py` | `figureS3_monitoring.png` |

Script names keep their earlier numbering. The output names follow the
current figure order, in which the task comparison is Figure 4, prices
Figure 5 and the resource boundary Figure 6.

Shared modules: `paths.py` (locations), `style.py` (palette, type, Elsevier
export rules and the audit gate), `maps.py` (map layers) and
`fig1_parts_common.py` (shared inputs of the Figure 1 parts). Figures are
190 mm wide, PNG at 1,000 dpi, with no title inside the artwork. The data
figures assert the counts reported in the manuscript and write nothing if any
differs.

## Source tables

`build_tables_statistics.py` and `build_tables_geography.py` copy derived
views from `SR_EVIDENCE` into `SR_FIGURE_DATA` (or `--out DIR`). They also
write the SHA-256 of every input and a grid summary to `provenance/` there.
Table names keep their historical numerical prefixes:

| Table | Built by | Used by |
| --- | --- | --- |
| `figure2_extent_grid.csv`, `figure2_pairs.csv.gz`, `figure2_sources.csv` | statistics | Figure 3 |
| `figure3_prices.csv`, `figure3_sources.csv` | statistics | Figure 5 |
| `figure4_phase.csv.gz`, `figure4_geography.csv` | statistics | Figure 6 |
| `figure5_sources.csv`, `figure5_families.csv` | statistics | Figure 4 |
| `figure2_anchor_counts.csv` | geography | Figures 2, 6 and S1 |
| `density_grids/<source>.json` | geography | Figures 2 and S1 |
| `figure1_design.json` | geography | design numbers quoted with Figure 1 |
| `figureS2_full_day_d.csv` | supplied with the data | Supplementary Fig. S2 |
| `figureS3_dublin_grid.csv`, `figureS3_dublin_daily.csv` | supplied with the data | Supplementary Fig. S3 |
| `basemap/ne_50m_land.geojson`, `basemap/ne_50m_admin_0_countries.geojson` | supplied with the data (Natural Earth) | Figures 1, 2 |
| `basemap/rome_osm.json`, `basemap/rome_traces.json` | `fetch_rome_layers.py` | Figure 1 parts |

Density grids come in two releases (`--grid-release`). Release v1 shows a cell
only if at least five dataset-defined entities were seen in it on one
registered day. Release v2 is the default and the one used by the current
figures: following the author decision of 2026-10-20 it shows every nonempty
cell. The builder checks that every cell shown in v1 reappears in v2 with the
same count.

`fetch_rome_layers.py` refreshes the two Rome layers of the Figure 1 parts:

```bash
python figures/fetch_rome_layers.py --points /path/to/rome_2014-02-21.bin
python figures/fetch_rome_layers.py --skip-traces   # OpenStreetMap layer only
```

It downloads OpenStreetMap streets, rivers, water and parks for the 6 km tile
from the public Overpass API, retrying with backoff when the server is busy.
It then extracts the taxi traces in that tile from 07:00 to 09:00 on
2014-02-21 from a local point-record file. The file is either the registered
binary point pack (checked against its registered size and SHA-256) or a CSV
with columns `x`, `y`, `t`, `entity`. Only coordinates relative to the tile
centre are written; taxi identifiers are not.

## Data notes and licences

- **Data are not included.** The source tables, the evidence archive, the
  basemap layers and the tile cache must be provided locally through the
  variables above.
- **Natural Earth** land and country polygons (1:50m) are in the public domain
  ([naturalearthdata.com](https://www.naturalearthdata.com)).
- **OpenStreetMap** data are © OpenStreetMap contributors and available under
  the Open Database Licence (ODbL 1.0). Figures that show them must carry the
  attribution "© OpenStreetMap contributors". A redistributed
  `rome_osm.json` remains under the ODbL.
- **Esri World Light Gray Canvas** tiles are fetched at run time by contextily
  from Esri's ArcGIS Online service and cached in `SR_TILE_CACHE`. Their use
  requires legitimate access under Esri's terms of use and the attribution
  stated by the provider, "Tiles © Esri — Esri, DeLorme, NAVTEQ"; the figure
  captions credit Esri and its data providers. Do not redistribute the cache.
- **Rome taxi trajectories** are restricted. Obtain them from their provider,
  CRAWDAD dataset roma/taxi (v. 2014-07-17),
  [doi:10.15783/C7QC7M](https://doi.org/10.15783/C7QC7M), distributed through
  IEEE DataPort, and follow its terms (acknowledgement, no re-identification).
  `rome_traces.json` is derived from them and may be shared only as those terms
  allow.
- All other trajectory sources enter the figures only as derived aggregates
  (count grids and tables) from the evidence archive. The figure scripts never
  read raw records.
