#!/usr/bin/env python3
"""
merge_acs_to_tracts.py

Joins ACS population data to TIGER/Line tract GeoJSON and computes population density.
Input:
- tl_2025_49_tract.geojson (tract polygons)
- utah_acs_population.json (ACS population per tract)
Output:
- tracts_population.geojson (tract polygons with population, land_km2, density_per_km2)
"""
import json
from pathlib import Path

TRACTS = Path("tl_2025_49_tract.geojson")
ACS = Path("utah_acs_population.json")
OUTPUT = Path("tracts_population.geojson")

# Load ACS population data
with ACS.open("r", encoding="utf-8") as f:
    acs_rows = json.load(f)
acs_map = {}
for row in acs_rows[1:]:
    # [NAME, B01003_001E, state, county, tract]
    state, county, tract = row[2], row[3], row[4]
    geoid = f"{state}{county}{tract}"
    try:
        pop = int(row[1])
    except Exception:
        pop = 0
    acs_map[geoid] = pop

# Load tract polygons
with TRACTS.open("r", encoding="utf-8") as f:
    tracts_geo = json.load(f)

out_feats = []
for feat in tracts_geo.get("features", []):
    props = feat.get("properties", {})
    geoid = props.get("GEOID")
    aland = props.get("ALAND")
    pop = acs_map.get(geoid, 0)
    try:
        land_m2 = float(aland)
        land_km2 = land_m2 / 1e6 if land_m2 and land_m2 > 0 else 0
        density = (pop / land_km2) if land_km2 > 0 else 0
    except Exception:
        land_km2 = 0
        density = 0
    props["population"] = pop
    props["land_km2"] = land_km2
    props["density_per_km2"] = density
    out_feats.append({"type": "Feature", "geometry": feat.get("geometry"), "properties": props})

out = {"type": "FeatureCollection", "features": out_feats}
OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {OUTPUT} with {len(out_feats)} tracts")
