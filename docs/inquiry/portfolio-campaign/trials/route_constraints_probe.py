"""Bounded T5 exploration; no production router or navigation recommendation."""

import hashlib
import json
import math
import os
import urllib.parse
import urllib.request
from pathlib import Path


OUT = Path(os.environ.get("FOUNDRY_TRIAL_OUTPUT", Path(__file__).parent / "t5"))
OUT.mkdir(parents=True, exist_ok=False)
A, C = (13.278, 52.508), (13.510, 52.365)
BS = [(13.417, 52.468), (13.441, 52.466)]


def distance(a, b):
    """Haversine separation in metres for continuity checks only."""
    lon1, lat1, lon2, lat2 = map(math.radians, [*a[:2], *b[:2]])
    h = math.sin((lat2-lat1)/2)**2
    h += math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 6371000*2*math.asin(min(1, math.sqrt(h)))


def route(name, start, end, avoid):
    params = {
        "lonlats": "|".join(",".join(map(str, point)) for point in [start, end]),
        "profile": "car-fast", "alternativeidx": "0", "format": "geojson",
        "profile:avoid_motorways": "true" if avoid else "false",
    }
    url = "https://brouter.de/brouter?" + urllib.parse.urlencode(params)
    record = {"name": name, "url": url, "params": params}
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            raw = response.read()
            record["http_status"] = response.status
        (OUT / f"{name}.json").write_bytes(raw)
        record["sha256"] = hashlib.sha256(raw).hexdigest()
        feature = json.loads(raw)["features"][0]
        properties = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]
        messages = properties["messages"]
        tag_column = messages[0].index("WayTags")
        tags = [r[tag_column] for r in messages[1:]]
        record.update(
            valid=len(coordinates) > 1,
            creator=properties.get("creator"),
            distance_m=float(properties["track-length"]),
            time_s=float(properties["total-time"]),
            motorway_tag_rows=sum("highway=motorway" in t for t in tags),
            start=coordinates[0][:2], end=coordinates[-1][:2],
            start_snap_m=distance(start, coordinates[0]),
            end_snap_m=distance(end, coordinates[-1]),
            geometry_sha256=hashlib.sha256(json.dumps(coordinates).encode()).hexdigest(),
        )
    except Exception as error:
        record.update(valid=False, error=f"{type(error).__name__}: {error}")
    print(json.dumps(record), flush=True)
    return record


records = [route("baseline", A, C, False), route("avoid-control", A, C, True)]
alternatives = []
for index, point in enumerate(BS, 1):
    first = route(f"b{index}-first", A, point, False)
    second = route(f"b{index}-second", point, C, True)
    records += [first, second]
    if first["valid"] and second["valid"]:
        join_gap = distance(first["end"], second["start"])
        in_area = all(13.407 <= p[0] <= 13.451 and 52.456 <= p[1] <= 52.478
                      for p in [first["end"], second["start"]])
        alternatives.append({
            "candidate": f"B{index}", "time_s": first["time_s"] + second["time_s"],
            "distance_m": first["distance_m"] + second["distance_m"],
            "join_gap_m": join_gap, "join_in_area": in_area,
            "avoided_leg_motorway_rows": second["motorway_tag_rows"],
            "eligible": join_gap <= 100 and in_area and second["motorway_tag_rows"] == 0,
        })
control = all(r["valid"] for r in records[:2]) and (
    records[0]["motorway_tag_rows"] > records[1]["motorway_tag_rows"]
    and records[0]["geometry_sha256"] != records[1]["geometry_sha256"]
)
eligible = [a for a in alternatives if a["eligible"]]
result = {
    "trial": "T5", "date": "2026-10-02", "requests": records,
    "positive_control": control, "alternatives": alternatives,
    "selected": min(eligible, key=lambda a: a["time_s"]) if eligible else None,
    "outcome": "SUPPORTED_NARROW_COMPOSITION" if control and eligible else "INCONCLUSIVE",
    "limits": ["synthetic task", "two sampled points, not continuous optimality",
               "no beauty or usability validation", "public service profile/version not pinned",
               "no safe-navigation or customer-demand inference"],
}
(OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "requests"}, indent=2))
