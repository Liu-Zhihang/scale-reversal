# Manuscript figures

Previews of the figures in *Rethinking uncertain geographic context and scale in urban trajectory data through hybrid quantum range queries*. The text under each heading is what the figure is for. Panel notes follow the manuscript captions. Counts are the published checks: 13,370 nonempty supported windows, 742 with Q < C, 17,592 adjacent-scale pairs, 1,060 forward reversals and 11 reverse crossings, all under the main prices (L1) and one preparation unless a caption says otherwise.

The repository landing page shows Figures 1, 3, 4 and 7. This page keeps the rest, so a reader can see every preview without scrolling through nine unexplained images on the front page. Supplementary Figure S1, the maps of the ten sources not enlarged in Figure 2, is redrawn by `figures/figS1_cities.py` and is not embedded here.

Redraw Figures 1–6 and S1–S3 with:

```bash
SR_FIGURE_DATA=evidence/figure_source SR_EVIDENCE=evidence python figures/make_all.py
```

## Figure 1. One space-time window, two decisions

One window does two jobs. It is the query whose two access routes are priced, and it is the background whose records estimate a held-out urban reading. Classical-led preparation resolves the K matches and then prepares the output state, at cost C. Quantum filtering, the hybrid quantum algorithm, prepares M candidates and repeats prepare-and-test about M/K times, at cost Q = P + (M/K)H. Both routes return the same state. Enlarging the window can reverse the sign of D = log₂(Q/C). The dashed arrow is the risk of choosing a background because retrieval is cheaper. The index, circuit and cost curves are schematic. Basemaps are Natural Earth; street data are © OpenStreetMap contributors (ODbL). The Rome taxi layer is not in this repository.

![Figure 1. One space-time window, two decisions](figures/figure1_framework.png)

## Figure 2. Global and city-level locations of the observations

Where the records are, and where the cheaper quantum windows sit. Panel (a) colours the 13 cities of the access cohort by the share of supported windows with Q < C. Open circles are Paris and Barcelona, which have none. Diamonds are the monitoring-only sources Zurich and Portici. Panel (b) enlarges the European cities. Panels (c)–(f) are Beijing (T-Drive), Rome, San Francisco and Rio de Janeiro, each 24 km wide. Teal is log₁₀ pooled records per km² on 250 m cells. Anchor circles are coloured by their own share of windows with Q < C; open circles have eligible windows but none with Q < C, and crosses have no eligible windows. Basemaps are Natural Earth and Esri World Light Gray Canvas.

![Figure 2. Global and city-level locations of the observations](figures/figure2_observation_geography.png)

## Figure 3. Enlarging the window can make quantum filtering the cheaper route

The main result on cost. Panel (a) is the share of nonempty, fully supported windows with Q < C on the width–duration grid. Panel (b) places all 17,592 adjacent pairs by Q/C at the smaller and the larger window. Warm bins are the 1,060 forward reversals, teal bins are all other pairs, and the dark points are the 11 reverse crossings. Panel (c) shows Q/C of the forward-reversal pairs before and after the enlargement; bars are medians and the dashed line is Q = C. Panel (d) is the forward-reversal share by source; open circles are the two sources with none. Overlapping windows are not independent replications.

![Figure 3. Enlarging the window can make quantum filtering the cheaper route](figures/figure3_reversal.png)

## Figure 4. Cheaper windows do not reconstruct urban readings better

Cost and analytical quality do not move together. Panel (a) is the share of enlargements whose reconstruction error got worse, among forward crossings and among comparable enlargements that did not cross, with 95% date-block intervals. Labels give forward pairs and positive dates. Ties are excluded. Panel (b) is the difference in percentage points. Positive values mean crossings worsened more often. Filled markers meet the prespecified rule of at least five points with an interval excluding zero. Open markers carry no information, which does not mean the shares are equivalent. The band is ±5 points. Intervals are descriptive and are not adjusted for multiplicity. Barcelona, Stellenbosch and Portici have no forward crossing. In the manuscript, mobile-monitoring estimates worsened 15.7 percentage points more often after a crossing than after a non-crossing enlargement, and speed reconstruction did not improve.

![Figure 4. Cheaper windows do not reconstruct urban readings better](figures/figure4_tasks.png)

## Figure 5. Prices move scale reversal but do not remove it

The reversal is not an artefact of one price list. Panel (a) counts forward-reversal pairs at each of 45 combinations of coherent-lookup and quantum-geometry prices; outlined cells are the four reporting points. Panel (b) is the median Q/C over the same 13,370 windows, above 15 in every combination. Panel (c) splits forward-reversal pairs at the reporting points into pairs retained from the main prices, new pairs, and main-price pairs lost because the smaller window also became favourable. Panel (d) is the forward-reversal share by source. Paris and Barcelona have none under the main prices and gain some at lower prices. Classical geometry, gate prices and repetitions stay fixed. The repricing is deterministic, not a hardware forecast.

![Figure 5. Prices move scale reversal but do not remove it](figures/figure5_prices.png)

## Figure 6. Reversals follow record accumulation and index consolidation, not simply the city centre

The ordering of a window follows how many records it collects and how the index groups them, not whether the anchor is downtown. Panel (a) plots all 13,370 supported windows by matching records K and by candidate purity per attempt cost. Warm points are the 742 favourable windows, dark teal points are the 589 won by classical whole-block acceptance, and light teal points are the other classical-led windows. The line is the approximate large-window reference Ψ* = 1/4.43. Panel (b) splits the change in ln Ψ into the three accounting terms of the manuscript. Panel (c) is the share of favourable windows at central, side and corner anchors under three denominators. Panel (d) is the same share by source. Bold names are sources where a side or corner anchor exceeds the centre. Open circles are sources without favourable windows.

![Figure 6. Reversals follow record accumulation and index consolidation](figures/figure6_boundary_geography.png)

## Figure 7. Checklist for evaluating a quantum urban data-access claim

The deliverable. Nine questions in four steps: fix the background by the task, compare like with like, test prices and reuse, and report the whole grid, including cities and windows without reversal. The evidence for each question is in the results. Question 7 refers to a separate earlier workload in which preparing the same query 100 times removed most of the quantum-favourable windows, because a classical result can be reused and a quantum state cannot. The checklist guides reporting. It is not a procurement score and it is not evidence that an urban service has been accelerated. The drawing is a black-and-white flowchart.

![Figure 7. Checklist for evaluating a quantum urban data-access claim](figures/figure7_checklist.png)

## Supplementary Figure S2. The same-answer intervention

A check that cost is not only a function of how many records a full day contains. One day and one timestamp permutation within 2 km cells, under fixed Packed R-tree routes, leaves every full-day answer set unchanged. Panel (a) is Q/C before and after for 279 windows, of which 277 change D. Panel (b) enlarges the boxed region. Panel (c) shows one Beijing and one Rome sign change. Panel (d) counts forward crossings among 2,540 pairs with both ends nonempty: 19 appear and 12 disappear. The check shows sensitivity of the tested representation. It does not separate travel organization from index layout.

![Supplementary Figure S2. The same-answer intervention](figures/figureS2_same_answer.png)

## Supplementary Figure S3. Jinan and Dublin monitoring contrasts

The two monitoring cities do not tell the same story, so the task result is not one directional rule. Panels (a)–(c) are Jinan: windows per extent among 144 device hold-out targets, the direction of error on forward crossings, and the date-level change in mean absolute error when a 2 km or 5 km background is extended from 1 h to 6 h. Panels (d)–(f) are the same for Dublin at 6 h, with widenings from 0.5 to 2 km and from 2 to 5 km. Rose is worse, teal is better, and diamonds are date means. Jinan keeps its native PM units. Dublin is in µg/m³.

![Supplementary Figure S3. Jinan and Dublin monitoring contrasts](figures/figureS3_monitoring.png)
