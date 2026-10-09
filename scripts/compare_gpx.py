"""One local route-transfer diagnostic; stdlib only, never contacts a service."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

Point = tuple[float, float]
Tracks = list[list[Point]]
R = 6371008.8


def distance(a: Point, b: Point) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(min(1, math.sqrt(h)))


def length(tracks: Tracks) -> float:
    return sum(
        distance(a, b)
        for track in tracks
        for a, b in zip(track, track[1:], strict=False)
    )


def parse(path: Path) -> tuple[Tracks, dict[str, object]]:
    raw = path.read_bytes()
    if (
        len(raw) > 10_000_000
        or b"<!DOCTYPE" in raw.upper()
        or b"<!ENTITY" in raw.upper()
    ):
        raise ValueError("GPX exceeds bounds or declares forbidden entities")
    root = ET.fromstring(raw)
    if root.tag.rsplit("}", 1)[-1] != "gpx":
        raise ValueError("Expected GPX root")
    tracks = []
    for segment in root.findall(".//{*}trkseg"):
        points = []
        for node in segment.findall("{*}trkpt"):
            point = (float(node.attrib["lat"]), float(node.attrib["lon"]))
            if (
                not all(math.isfinite(x) for x in point)
                or not -90 <= point[0] <= 90
                or not -180 <= point[1] <= 180
            ):
                raise ValueError("Invalid coordinate")
            points.append(point)
        if points:
            tracks.append(points)
    if not tracks or not any(len(t) > 1 for t in tracks):
        raise ValueError("No usable detailed track segments")
    return tracks, {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "tracks": len(root.findall("{*}trk")),
        "segments": len(tracks),
        "track_points": sum(map(len, tracks)),
        "route_points": len(root.findall(".//{*}rtept")),
        "timestamps": len(root.findall(".//{*}time")),
        "segment_lengths_km": [round(length([t]) / 1000, 3) for t in tracks],
    }


def samples(tracks: Tracks, spacing: float = 200) -> list[tuple[float, Point]]:
    result = []
    cumulative = 0.0
    for track in tracks:
        result.append((cumulative, track[0]))
        target = spacing
        along = 0.0
        for a, b in zip(track, track[1:], strict=False):
            span = distance(a, b)
            while span > 0 and target <= along + span:
                fraction = (target - along) / span
                result.append(
                    (
                        cumulative + target,
                        (
                            a[0] + fraction * (b[0] - a[0]),
                            a[1] + fraction * (b[1] - a[1]),
                        ),
                    )
                )
                target += spacing
            along += span
        cumulative += along
        result.append((cumulative, track[-1]))
    return result


def deviations(source: Tracks, target: Tracks) -> list[tuple[float, float]]:
    # Equirectangular local projection for nearest-segment distances. Haversine
    # remains the distance baseline. France-scale distortion <1% near tracks.
    lat0 = math.radians(
        sum(p[0] for t in source + target for p in t) / sum(map(len, source + target))
    )

    def project(p: Point) -> Point:
        return (R * math.radians(p[1]) * math.cos(lat0), R * math.radians(p[0]))

    segments = [
        (project(a), project(b))
        for track in target
        for a, b in zip(track, track[1:], strict=False)
    ]
    output = []
    for along, p in samples(source):
        x, y = project(p)
        minimum = float("inf")
        for (ax, ay), (bx, by) in segments:
            dx = bx - ax
            dy = by - ay
            norm = dx * dx + dy * dy
            t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / norm)) if norm else 0
            squared = (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2
            if squared < minimum:
                minimum = squared
        output.append((along, math.sqrt(minimum)))
    return output


def stats(values: list[tuple[float, float]]) -> dict[str, object]:
    distances = sorted(v for _, v in values)
    return {
        "samples": len(values),
        "median_m": round(distances[len(distances) // 2], 1),
        "p95_m": round(distances[int(0.95 * (len(distances) - 1))], 1),
        "max_m": round(distances[-1], 1),
        "fraction_within": {
            str(t): round(sum(d <= t for d in distances) / len(distances), 4)
            for t in (25, 50, 100)
        },
        "largest_sections": [
            {"along_km": round(a / 1000, 2), "deviation_m": round(d, 1)}
            for a, d in sorted(values, key=lambda v: -v[1])[:10]
        ],
    }


def controls() -> None:
    dense = [[(48.0, 2.0 + i * 0.001) for i in range(11)]]
    sparse = [[dense[0][0], dense[0][-1]]]
    assert max(d for _, d in deviations(dense, dense)) < 0.001
    assert max(d for _, d in deviations(dense, sparse)) < 0.001
    detour = [[(48.0, 2.0), (48.01, 2.005), (48.0, 2.01)]]
    assert max(d for _, d in deviations(detour, dense)) > 1000
    split = [[(48.0, 2.0), (48.0, 2.001)], [(48.0, 2.1), (48.0, 2.101)]]
    assert length(split) < 200 and length([split[0] + split[1]]) > 7000
    assert max(d for _, d in deviations([[(48.0, 2.05), (48.0, 2.051)]], split)) > 3000


def compare(a_path: Path, b_path: Path, output: Path) -> dict[str, object]:
    controls()
    a, meta_a = parse(a_path)
    b, meta_b = parse(b_path)
    direct = distance(a[0][0], b[0][0]) + distance(a[-1][-1], b[-1][-1])
    reverse = distance(a[0][0], b[-1][-1]) + distance(a[-1][-1], b[0][0])
    reversed_b = reverse < direct
    if reversed_b:
        b = [list(reversed(t)) for t in reversed(b)]
    da = length(a) / 1000
    db = length(b) / 1000
    delta = db - da
    equivalent = delta / (da / 275)
    simplified = []
    ratio = max(1, round(sum(map(len, a)) / 479))
    for t in a:
        points = t[::ratio]
        if points[-1] != t[-1]:
            points.append(t[-1])
        simplified.append(points)
    summary = {
        "schema_version": "gpx-comparison/v1",
        "liberty": meta_a,
        "68degrees": meta_b,
        "length_km": {
            "liberty": round(da, 3),
            "68degrees": round(db, 3),
            "delta": round(delta, 3),
        },
        "start_difference_m": round(distance(a[0][0], b[0][0]), 1),
        "end_difference_m": round(distance(a[-1][-1], b[-1][-1]), 1),
        "direction_normalized": reversed_b,
        "liberty_to_68": stats(deviations(a, b)),
        "68_to_liberty": stats(deviations(b, a)),
        "downsample_control": stats(deviations(a, simplified)),
        "downsample_length_loss_km": round(da - length(simplified) / 1000, 3),
        "reported_eta_minutes": [275, 364],
        "implied_mean_kmh": [round(da / (275 / 60), 2), round(db / (364 / 60), 2)],
        "extra_minutes_at_liberty_mean_speed": round(equivalent, 2),
        "hypothesis": "supported" if equivalent >= 44.5 else "weakened",
        "limits": (
            "No timestamps, no road metadata, no ETA accuracy or "
            "exact-road attribution. Nearest-segment projection and "
            "sampling are approximate; downsampling is one control, not "
            "a guaranteed error bound."
        ),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "route-summary.json").write_text(json.dumps(summary, indent=2))
    points = [p for tracks in (a, b) for t in tracks for p in t]
    minlat = min(p[0] for p in points)
    maxlat = max(p[0] for p in points)
    minlon = min(p[1] for p in points)
    maxlon = max(p[1] for p in points)

    def line(t: list[Point]) -> str:
        return " ".join(
            f"{25 + 950 * (p[1] - minlon) / (maxlon - minlon):.2f},"
            f"{25 + 750 * (maxlat - p[0]) / (maxlat - minlat):.2f}"
            for p in t
        )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 '
        '800"><rect width="1000" height="800" fill="white"/>'
    )
    for tracks, color in [(a, "#2563eb"), (b, "#ef4444")]:
        for t in tracks:
            svg += (
                f'<polyline points="{line(t)}" fill="none" stroke="{color}" '
                'stroke-width="2" opacity=".7"/>'
            )
    svg += "</svg>"
    (output / "overlay.svg").write_text(svg)
    (output / "route-report.html").write_text(
        (
            '<!doctype html><meta charset="utf-8"><title>Private route '
            "comparison</title><h1>Private offline route "
            "comparison</h1><p>Blue: Liberty Rider. Red: 68°. No "
            "basemap/network.</p>"
        )
        + svg
        + "<pre>"
        + html.escape(json.dumps(summary, indent=2))
        + "</pre>"
    )
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("liberty", type=Path)
    p.add_argument("degrees", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    print(json.dumps(compare(args.liberty, args.degrees, args.output), indent=2))
