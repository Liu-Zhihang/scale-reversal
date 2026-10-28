# scale-reversal

Computations for the manuscript *Rethinking uncertain geographic context and
scale in urban trajectory data through hybrid quantum range queries*. This
package does not reimplement the query engine. Window evaluation, access-route
accounting, pricing and repricing all call
[qrq](https://pypi.org/project/qrq/) 0.2.0, a general library for quantum
range queries over spatiotemporal records. qrq contains no study-specific
code; everything particular to this study lives here.

## What is here

* The registered window grid: six widths, four durations, nine anchors and
  three time centres, and the adjacent-scale pairs built from it.
* Readers for the sealed evidence archive and checks that reproduce the
  published counts: 13,370 nonempty windows, 742 with `Q < C`, 17,592
  adjacent pairs, 1,060 forward and 11 reverse reversals.
* The 45-point price sweep and its reporting points.
* The amplitude-amplification sensitivity.
* The reconstruction-task comparison and its date-block bootstrap.
* Figure scripts that redraw the manuscript figures from the source tables
  (`figures/README.md`).

## Install

```bash
pip install qrq==0.2.0
pip install ".[test]"
```

Figure rendering needs the extra `figures` dependencies (`pip install ".[figures]"`).

## Reproduce the published numbers

Derived tables, per-tree cost ledgers and figure source tables are in
`evidence/`. Raw trajectory and monitoring records are not included.
With the archive root in `SR_EVIDENCE`:

```bash
SR_EVIDENCE=evidence python -m scale_reversal all --check
```

Exit status 0 means the cohort, the price sweep, the
amplitude-amplification sensitivity and the task comparison all match the
published numbers. `pytest` without `SR_EVIDENCE` runs the synthetic tests
and skips the sealed ones. Details, artefact overrides and numerical notes
are in `docs/reproduction.md`; the public sources are listed in
`docs/data_access.md`.

## Figures

The landing page keeps the four figures that carry the argument. Each one is
followed by what it shows. Geography, the price sweep, the resource boundary
and the supplementary checks are explained in
[docs/figures.md](docs/figures.md), with the same previews. The scripts in
`figures/` redraw Figures 1–6 and Supplementary Figures S1–S3 from the source
tables. Figure 7 is the evaluation checklist; its preview is the black-and-white
flowchart used in the manuscript.

### Figure 1. One space-time window, two decisions

The same window is both a priced query and the background of a held-out urban
estimate. Classical-led preparation resolves the matching records and then
prepares the output, at cost C. Quantum filtering, the hybrid quantum
algorithm evaluated here, prepares a frontier of M candidates and repeats
prepare-and-test about M/K times, at cost Q. Enlarging the window can reverse
which route is cheaper. The dashed arrow marks the risk of choosing a
background because it lowers access cost. The index, circuit and cost curves
are schematic. The Rome taxi layer is not redistributed with this repository.

![One space-time window, two decisions](docs/figures/figure1_framework.png)

### Figure 3. Enlarging the window can make quantum filtering the cheaper route

Under the main prices, enlarging one step turned quantum filtering from the
costlier route into the cheaper one in 1,060 of 17,592 adjacent-scale pairs,
across 11 of 13 cities. Warm bins in panel (b) are those forward reversals;
the dark points are the 11 crossings in the opposite direction. Paris and
Barcelona, the open circles in panel (d), have none. Overlapping windows are
not independent replications, and a lower quantum cost is not yet a claim
about the urban reading.

![Enlarging the window can make quantum filtering the cheaper route](docs/figures/figure3_reversal.png)

### Figure 4. Cheaper windows do not reconstruct urban readings better

Crossing into lower quantum cost did not improve speed reconstruction.
Mobile-monitoring estimates worsened more often than after comparable
enlargements that did not cross, by 15.7 percentage points in the reported
contrast. Panel (b) is that difference. Filled markers meet the prespecified
rule; open markers carry no information, which does not mean the two shares
are equivalent. Barcelona, Stellenbosch and Portici have no forward crossing.

![Cheaper windows do not reconstruct urban readings better](docs/figures/figure4_tasks.png)

### Figure 7. Checklist for a quantum urban data-access claim

Nine questions run in four steps: fix the background by the task before any
cost is seen, compare routes that return the same output, test a grid of
prices and how often the query must be prepared again, and report every width,
duration and negative result. The checklist guides reporting. It is not a
procurement score and does not say that a service is ready.

![Checklist for a quantum urban data-access claim](docs/figures/figure7_checklist.png)

```bash
SR_FIGURE_DATA=evidence/figure_source SR_EVIDENCE=evidence python figures/make_all.py
```

See `figures/README.md` and [docs/figures.md](docs/figures.md). The Rome
trajectory layer of Figure 1 needs the taxi records from their provider and
is not redistributed.

## License

MIT, see `LICENSE`. Citation metadata is in `CITATION.cff`.
