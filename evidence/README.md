# Derived evidence

This directory holds the derived tables, per-tree cost ledgers and figure
source tables for the manuscript. Raw trajectory and monitoring records are
not included. The Rome taxi traces used for one layer of Figure 1 are not
included either.

Set `SR_EVIDENCE` to this directory and `SR_FIGURE_DATA` to
`figure_source`. See `docs/reproduction.md`.

Machine logs and run-launch records were left out because they name local
paths. Ledger lines contain window identifiers, sizes and costs, not record
coordinates. Registered window bounds in `inputs/queries` are in a projected
metre CRS.
