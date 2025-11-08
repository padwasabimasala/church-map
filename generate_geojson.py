#!/usr/bin/env python3
"""
generate_geojson.py

Reads `output.json` (an array of places with `lat` and `lon`) and writes
`churches.geojson` as a GeoJSON FeatureCollection suitable for Leaflet.

Usage: python3 generate_geojson.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "output.json"
OUTPUT = ROOT / "churches.geojson"


def make_feature(item):
    # Expect numeric lon/lat
    lon = item.get("lon")
    lat = item.get("lat")
    if lon is None or lat is None:
        return None

    props = {}
    # Copy a selection of useful properties (avoid massive nested raw dumps)
    keys = [
        "name",
        "formatted",
        "address_line1",
        "address_line2",
        "street",
        "housenumber",
        "city",
        "state",
        "postcode",
        "country",
        "country_code",
        "website",
        "place_id",
        "categories",
    ]
    for k in keys:
        if k in item:
            props[k] = item[k]

    # contact.phone often nested in contact
    contact = item.get("contact")
    if contact and isinstance(contact, dict):
        phone = contact.get("phone")
        if phone:
            props["phone"] = phone

    # flatten some nested common fields
    if "place_of_worship" in item and isinstance(item["place_of_worship"], dict):
        props.update({"place_of_worship." + k: v for k, v in item["place_of_worship"].items()})

    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": props,
    }
    return feature


def main():
    if not INPUT.exists():
        print(f"Input file not found: {INPUT}")
        return

    data = json.loads(INPUT.read_text(encoding="utf-8"))
    features = []
    skipped = 0
    for item in data:
        f = make_feature(item)
        if f is None:
            skipped += 1
            continue
        features.append(f)

    geo = {"type": "FeatureCollection", "features": features}
    OUTPUT.write_text(json.dumps(geo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(features)} features (skipped {skipped}).")


if __name__ == "__main__":
    main()
