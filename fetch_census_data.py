#!/usr/bin/env python3
"""
fetch_census_data.py

Fetches census tracts overlapping the churches in `churches.geojson` using
TIGERweb, pulls population (ACS 5-year) from the Census API, computes
population density (people per sq km) and writes `tracts_population.geojson`.

Usage: python3 fetch_census_data.py

Notes:
- Requires internet access. Uses the TIGERweb REST endpoint and the Census API.
- Default ACS year is 2021 (modify ACS_YEAR variable if needed).
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
CHURCHES = ROOT / "churches.geojson"
OUTPUT = ROOT / "tracts_population.geojson"

ACS_YEAR = "2021"
ACS_VAR = "B01003_001E"  # total population


def read_churches_bbox():
    if not CHURCHES.exists():
        print(f"{CHURCHES} not found", file=sys.stderr)
        sys.exit(1)
    data = json.loads(CHURCHES.read_text(encoding='utf-8'))
    coords = []
    for f in data.get('features', []):
        g = f.get('geometry') or {}
        if g.get('type') == 'Point':
            lon, lat = g.get('coordinates', [None, None])
            if lon is not None and lat is not None:
                coords.append((lon, lat))
    if not coords:
        print('No point coordinates found in churches.geojson', file=sys.stderr)
        sys.exit(1)
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    minx, maxx = min(lons), max(lons)
    miny, maxy = min(lats), max(lats)
    # expand bbox by a small margin (0.1 deg)
    dx = (maxx - minx) * 0.2 if maxx - minx > 0 else 0.1
    dy = (maxy - miny) * 0.2 if maxy - miny > 0 else 0.1
    return (minx - dx, miny - dy, maxx + dx, maxy + dy)


def fetch_tiger_tracts(bbox):
    base = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts/MapServer/0/query'
    params = {
        'where': '1=1',
        'geometry': f'{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}',
        'geometryType': 'esriGeometryEnvelope',
        'inSR': '4326',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'GEOID,STATEFP,COUNTYFP,ALAND',
        'returnGeometry': 'true',
        'f': 'geojson'
    }
    url = base + '?' + urllib.parse.urlencode(params)
    print('Fetching tracts from TIGERweb...')
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    return data


def fetch_acs_populations(statefp, countyfp):
    # Fetch ACS population for all tracts in the county
    base = f'https://api.census.gov/data/{ACS_YEAR}/acs/acs5'
    params = {
        'get': f'NAME,{ACS_VAR}',
        'for': 'tract:*',
        'in': f'state:{statefp}%20county:{countyfp}'
    }
    url = base + '?' + urllib.parse.urlencode(params)
    print(f'Fetching ACS population for state {statefp} county {countyfp}...')
    with urllib.request.urlopen(url) as resp:
        arr = json.load(resp)
    # first row are headers
    headers = arr[0]
    rows = arr[1:]
    mapping = {}
    for r in rows:
        # r example: [NAME, pop, state, county, tract]
        try:
            name = r[0]
            pop = int(r[1]) if r[1] not in (None, '') else 0
            state = r[-3]
            county = r[-2]
            tract = r[-1]
            geoid = f"{state}{county}{tract}"
            mapping[geoid] = pop
        except Exception:
            continue
    return mapping


def main():
    bbox = read_churches_bbox()
    tracts_geo = fetch_tiger_tracts(bbox)
    features = tracts_geo.get('features', [])
    if not features:
        print('No tracts returned -- try expanding bbox', file=sys.stderr)
        sys.exit(1)

    # group by state/county to fetch ACS in batches
    to_fetch = {}
    for f in features:
        props = f.get('properties', {})
        st = props.get('STATEFP')
        co = props.get('COUNTYFP')
        if st and co:
            to_fetch.setdefault((st, co), []).append(f)

    pop_map = {}
    for (st, co), feats in to_fetch.items():
        mapping = fetch_acs_populations(st, co)
        pop_map.update(mapping)

    # attach population and density
    out_feats = []
    for f in features:
        props = f.get('properties', {})
        geoid = props.get('GEOID')
        aland = props.get('ALAND')
        try:
            pop = int(pop_map.get(geoid, 0))
        except Exception:
            pop = 0
        # ALAND is in square meters; convert to sq km
        try:
            land_m2 = float(aland)
            land_km2 = land_m2 / 1e6 if land_m2 and land_m2 > 0 else 0
            density = (pop / land_km2) if land_km2 > 0 else 0
        except Exception:
            land_km2 = 0
            density = 0
        props['population'] = pop
        props['land_km2'] = land_km2
        props['density_per_km2'] = density
        out_feats.append({'type': 'Feature', 'geometry': f.get('geometry'), 'properties': props})

    out = {'type': 'FeatureCollection', 'features': out_feats}
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {OUTPUT} with {len(out_feats)} tracts')


if __name__ == '__main__':
    main()
