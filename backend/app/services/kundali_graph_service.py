"""Transform kundali engine output into SVG-friendly graph payload."""

from __future__ import annotations

from datetime import datetime
import math

from app.calendar.kundali import compute_kundali


def _polar(cx: float, cy: float, radius: float, angle_deg: float) -> tuple[float, float]:
    rad = math.radians(angle_deg)
    return (round(cx + radius * math.cos(rad), 3), round(cy + radius * math.sin(rad), 3))


def build_kundali_graph(*, birth_dt: datetime, latitude: float, longitude: float, timezone_name: str) -> dict:
    data = compute_kundali(birth_dt, lat=latitude, lon=longitude, tz_name=timezone_name)

    center_x, center_y = 200.0, 200.0
    house_radius = 140.0
    graha_radius = 110.0

    house_nodes = []
    for house in data.get("houses", []):
        house_no = int(house.get("house_number", 1))
        # 1st house starts at top and proceeds clockwise.
        angle = -90 + (house_no - 1) * 30
        x, y = _polar(center_x, center_y, house_radius, angle)
        house_nodes.append(
            {
                "id": f"house_{house_no}",
                "house_number": house_no,
                "label": house.get("rashi_english") or house.get("rashi_sanskrit"),
                "rashi_sanskrit": house.get("rashi_sanskrit"),
                "rashi_english": house.get("rashi_english"),
                "occupants": house.get("occupants", []),
                "x": x,
                "y": y,
            }
        )

    graha_nodes = []
    for idx, (gid, graha) in enumerate((data.get("grahas") or {}).items()):
        longitude_deg = float(graha.get("longitude", 0.0) or 0.0)
        angle = -90 + longitude_deg
        x, y = _polar(center_x, center_y, graha_radius, angle)
        graha_nodes.append(
            {
                "id": gid,
                "label": graha.get("name_english") or gid.title(),
                "name_sanskrit": graha.get("name_sanskrit"),
                "rashi": graha.get("rashi_english"),
                "longitude": longitude_deg,
                "is_retrograde": bool(graha.get("is_retrograde")),
                "dignity": graha.get("dignity"),
                "x": x,
                "y": y,
                "ring_index": idx,
            }
        )

    aspect_edges = []
    for aspect in data.get("aspects", []):
        source = aspect.get("from")
        target = aspect.get("to")
        if not source or not target:
            continue
        aspect_edges.append(
            {
                "id": f"{source}->{target}:{aspect.get('aspect_angle', 0)}",
                "source": source,
                "target": target,
                "strength": aspect.get("strength", 0),
                "nature": aspect.get("nature", "neutral"),
                "aspect_angle": aspect.get("aspect_angle"),
                "orb": aspect.get("orb"),
            }
        )

    yoga_clusters = [
        {
            "id": row.get("id"),
            "name": row.get("name"),
            "status": row.get("status"),
            "reason": row.get("reason"),
            "type": "yoga",
        }
        for row in data.get("yogas", [])
    ]

    dosha_markers = [
        {
            "id": row.get("id"),
            "name": row.get("name"),
            "status": row.get("status"),
            "severity": row.get("severity"),
            "reason": row.get("reason"),
            "type": "dosha",
        }
        for row in data.get("doshas", [])
    ]

    return {
        "datetime": data.get("birth_datetime"),
        "location": data.get("location"),
        "lagna": data.get("lagna"),
        "layout": {
            "viewbox": "0 0 400 400",
            "center": {"x": center_x, "y": center_y},
            "house_radius": house_radius,
            "graha_radius": graha_radius,
            "house_nodes": house_nodes,
            "graha_nodes": graha_nodes,
            "aspect_edges": aspect_edges,
            "yoga_clusters": yoga_clusters,
            "dosha_markers": dosha_markers,
        },
        "insight_blocks": [
            {
                "id": "lagna_summary",
                "title": "Lagna Orientation",
                "summary": f"Lagna is {data.get('lagna', {}).get('rashi_english', 'unknown')}.",
            },
            {
                "id": "aspect_summary",
                "title": "Aspect Network",
                "summary": f"{len(aspect_edges)} major aspect links are active in this chart.",
            },
        ],
        "quality_band": "validated",
        "method_profile": "kundali_graph_v1_svg",
    }
