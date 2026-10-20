"""Fetch the two data layers of the Figure 1 city part, once, into the figure data.

1. OpenStreetMap streets, river and parks for a square tile around the Rome
   reference point (Overpass API; data (c) OpenStreetMap contributors, ODbL).
2. Real taxi trajectories in the same tile, read from a local copy of the
   registered Rome point records for one source-day. The Rome taxi
   trajectories are restricted: obtain them from their provider; they are not
   part of this repository. Only coordinates relative to the tile centre
   (x, y, t) are written; taxi identifiers are used to join records into
   traces and are not written. Consecutive records are joined only when they
   are at most 120 s and 800 m apart.

The point-record file comes from --points or the SR_ROME_POINTS environment
variable, in one of two forms:
- the registered binary point pack: little-endian records of x, y, t (float64),
  entity (int64) and source ordinal (uint64), with x and y in metres in the
  source's registered UTM zone and t in seconds of the day. Its size and
  SHA-256 must match the registered source-day in the evidence archive;
- a CSV file with columns x, y, t and entity in the same units, for which no
  registered checksum exists.

Writes rome_osm.json and rome_traces.json to SR_FIGURE_DATA/basemap (or --out).
--skip-osm and --skip-traces refresh one layer only; the Overpass request needs
network access.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import time

import numpy as np
import pandas as pd
import pyproj
import requests

import maps as M
import style as S

HALF_M = 3000
OFFSET_M = (-1500.0, 1400.0)   # tile centre relative to the reference point: densest trajectories
DATE = "2014-02-21"
T0, T1 = 7 * 3600, 9 * 3600
MAX_TAXIS = 90                 # taxis with the most records in the tile and time window
MAX_GAP_S, MAX_STEP_M = 120, 800
MIN_RECORDS = 5                # shorter pieces are dropped
OVERPASS = "https://overpass-api.de/api/interpreter"
CLIENT_ID = "urban-figure/1.0 (academic research)"
POINT_RECORD = np.dtype([("x", "<f8"), ("y", "<f8"), ("t", "<f8"), ("entity", "<i8"), ("source_ordinal", "<u8")])


def tile():
    """Rome geometry and the tile centre in its registered UTM zone."""
    geo = M.geometry()["rome_taxi"]
    return geo, geo["x"] + OFFSET_M[0], geo["y"] + OFFSET_M[1]


def fetch_osm(geo, cx, cy, out):
    to_ll = pyproj.Transformer.from_crs(geo["epsg"], 4326, always_xy=True)
    lon0, lat0 = to_ll.transform(cx - HALF_M, cy - HALF_M)
    lon1, lat1 = to_ll.transform(cx + HALF_M, cy + HALF_M)
    south, west, north, east = min(lat0, lat1), min(lon0, lon1), max(lat0, lat1), max(lon0, lon1)
    bbox = f"{south:.5f},{west:.5f},{north:.5f},{east:.5f}"
    query = f"""[out:json][timeout:180];
(way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|pedestrian)$"]({bbox});
 way["waterway"="river"]({bbox}); way["natural"="water"]({bbox}); way["leisure"="park"]({bbox}););
out geom;"""
    # The public Overpass endpoint rejects requests that carry only the HTTP
    # library's default client identification, so replace it with one naming the use.
    session = requests.Session()
    default_id = requests.utils.default_user_agent()
    replaced = {key: CLIENT_ID for key, value in session.headers.items() if value == default_id}
    assert replaced, "no default client identification header to replace"
    session.headers.update(replaced)
    # A busy public endpoint answers 429 or 5xx and asks clients to retry with
    # exponential backoff: wait 15, 30, 60 and 120 s before giving up.
    for attempt in range(5):
        reply = session.post(OVERPASS, data={"data": query}, timeout=300)
        if reply.status_code not in (429, 502, 503, 504) or attempt == 4:
            break
        print(f"Overpass busy (HTTP {reply.status_code}); retrying in {15 * 2 ** attempt} s", flush=True)
        time.sleep(15 * 2 ** attempt)
    reply.raise_for_status()
    osm = reply.json()
    osm["tile"] = {"epsg": geo["epsg"], "centre_xy": [cx, cy], "half_m": HALF_M, "offset_from_reference_m": OFFSET_M}
    (out / "rome_osm.json").write_text(json.dumps(osm))
    print("osm elements", len(osm["elements"]))


def read_points(path):
    """Point records of the Rome source-day; the binary pack must match its registration."""
    if path.suffix.lower() == ".csv":
        table = pd.read_csv(path, usecols=["x", "y", "t", "entity"])
        a = np.zeros(len(table), dtype=POINT_RECORD)
        for name in ("x", "y", "t", "entity"):
            a[name] = table[name].to_numpy()
        print("CSV point records: no registered checksum to compare")
        return a
    case = next(c for c in json.loads((M.M1_INPUTS / "cases.json").read_text())
                if c["source_id"] == "rome_taxi" and c["date"] == DATE)
    data = path.read_bytes()
    assert len(data) == case["point_bytes"] and hashlib.sha256(data).hexdigest() == case["point_sha256"], \
        f"{path.name} is not the registered Rome point pack for {DATE}"
    return np.frombuffer(data, dtype=POINT_RECORD)


def extract_traces(a, cx, cy):
    """Traces of the taxis with the most records in the tile from T0 to T1, relative to the tile centre."""
    h = HALF_M
    m = (np.abs(a["x"] - cx) <= h) & (np.abs(a["y"] - cy) <= h) & (a["t"] >= T0) & (a["t"] < T1)
    b = a[m]
    b = b[np.lexsort((b["t"], b["entity"]))]
    ents, counts = np.unique(b["entity"], return_counts=True)
    traces = []
    for e in ents[np.argsort(-counts)][:MAX_TAXIS]:
        s = b[b["entity"] == e]
        xs, ys, ts = s["x"] - cx, s["y"] - cy, s["t"]
        seg = [[xs[0], ys[0], ts[0]]]
        for i in range(1, len(s)):
            if ts[i] - ts[i - 1] <= MAX_GAP_S and np.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]) <= MAX_STEP_M:
                seg.append([xs[i], ys[i], ts[i]])
            else:
                if len(seg) >= MIN_RECORDS:
                    traces.append(seg)
                seg = [[xs[i], ys[i], ts[i]]]
        if len(seg) >= MIN_RECORDS:
            traces.append(seg)
    traces = [[[round(float(x), 1), round(float(y), 1), round(float(t), 1)] for x, y, t in tr] for tr in traces]
    return dict(date=DATE, window_s=[T0, T1], records=int(m.sum()), taxis=int(len(ents)), traces=traces)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--points", type=Path, default=os.environ.get("SR_ROME_POINTS") or None,
                        help="local Rome point-record file for 2014-02-21 (default: SR_ROME_POINTS)")
    parser.add_argument("--out", type=Path, help="output directory (default: SR_FIGURE_DATA/basemap)")
    parser.add_argument("--skip-osm", action="store_true", help="keep the existing rome_osm.json")
    parser.add_argument("--skip-traces", action="store_true", help="keep the existing rome_traces.json")
    args = parser.parse_args(argv)
    if not args.skip_traces and args.points is None:
        parser.error("pass --points or set SR_ROME_POINTS to the Rome point records, or use --skip-traces")
    out = args.out.expanduser() if args.out else S.SOURCE / "basemap"
    out.mkdir(parents=True, exist_ok=True)
    geo, cx, cy = tile()
    if not args.skip_osm:
        fetch_osm(geo, cx, cy, out)
    if not args.skip_traces:
        traces = extract_traces(read_points(args.points.expanduser()), cx, cy)
        (out / "rome_traces.json").write_text(json.dumps(traces))
        print("records", traces["records"], "taxis", traces["taxis"], "traces", len(traces["traces"]))


if __name__ == "__main__":
    main()
