#!/usr/bin/env python
import requests
import time
import json

API_KEY = "990f45fdbdd647e4aafbcc204a461b4f"


def get_worship_places(state, county):
    #lat, lon = get_coords(state, county)
    lat, lon = [-111.69107185434031, 40.177058]
    # https://api.geoapify.com/v2/places?PARAMS
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "religion.place_of_worship",
        "filter": f"circle:{lon},{lat},20000",  # radius in meters (20km)
        "limit": 1000,
        "apiKey": API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return [f["properties"] for f in r.json()["features"]]

def get_place_id(text):
    res = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'datasource': {'sourcename': 'openstreetmap', 'attribution': '© OpenStreetMap contributors', 'license': 'Open Database License', 'url': 'https://www.openstreetmap.org/copyright'}, 'other_names': {'name:ta': 'யூட்டா', 'alt_name': 'Utah'}, 'country': 'United States', 'country_code': 'us', 'state': 'Utah', 'county': 'Utah County', 'iso3166_2': 'US-UT', 'lon': -111.69107185434031, 'lat': 40.177058, 'state_code': 'UT', 'result_type': 'county', 'formatted': 'Utah County, UT, United States of America', 'address_line1': 'Utah County, UT', 'address_line2': 'United States of America', 'category': 'administrative', 'timezone': {'name': 'America/Denver', 'offset_STD': '-07:00', 'offset_STD_seconds': -25200, 'offset_DST': '-06:00', 'offset_DST_seconds': -21600, 'abbreviation_STD': 'MST', 'abbreviation_DST': 'MDT'}, 'plus_code': '85GC58G5+RH', 'rank': {'importance': 0.5109925914383722, 'popularity': 1.1963814831595563, 'confidence': 1, 'match_type': 'full_match'}, 'place_id': '51f96471853aec5bc05962bf27d6a9164440f00101f901f29d1a0000000000c00209'}, 'geometry': {'type': 'Point', 'coordinates': [-111.69107185434031, 40.177058]}, 'bbox': [-112.2141911, 39.776246, -110.857647, 40.577914]}], 'query': {'text': 'Utah County, Utah, USA', 'parsed': {'county': 'utah county', 'state': 'utah', 'country': 'usa', 'expected_type': 'county'}}}
    return '51f96471853aec5bc05962bf27d6a9164440f00101f901f29d1a0000000000c00209'
    url = f"https://api.geoapify.com/v1/geocode/search"
    params = {"text": text, "apiKey": API_KEY}
    r = requests.get(url, params=params)
    r.raise_for_status()
    res = r.json()
    print(res)
    return res["results"][0]["place_id"]

def fetch_coffee_shops(state, county, limit=500):
    region = f"{county}, {state}, USA"
    pid = get_place_id(region)
    category = "catering.cafe"
    category = "religion.christian"
    all_places = []
    offset = 0
    while True:
        url = f"https://api.geoapify.com/v2/places"
        params = {
            "categories": category,
            "filter": f"place:{pid}",
            "limit": 100,
            "offset": offset,
            "apiKey": API_KEY
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json().get("features", [])
        if not data:
            break
        all_places.extend([f["properties"] for f in data])
        offset += len(data)
        if offset >= limit:
            break
        time.sleep(0.2)
        break
    return all_places

def main(limit=10):
    category = "religion.christian"
    all_places = []
    offset = 0
    pid = '51f96471853aec5bc05962bf27d6a9164440f00101f901f29d1a0000000000c00209'
    while True:
        url = f"https://api.geoapify.com/v2/places"
        params = {
            "categories": category,
            "filter": f"place:{pid}",
            "limit": limit,
            "offset": offset,
            "apiKey": API_KEY
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json().get("features", [])
        if not data:
            break
        all_places.extend([f["properties"] for f in data])
        offset += len(data)
        if offset >= limit:
            break
        time.sleep(0.2)
        break
    return all_places

def write(data):
    with open("output.json", "w") as f:
        json.dump(data, f, indent=2)

def main():
    try:
        place_id = '51f96471853aec5bc05962bf27d6a9164440f00101f901f29d1a0000000000c00209'
        limit = 100
        offset = 0
        maxlimit = 10000
        all_places = []
        while True:
            url = f'https://api.geoapify.com/v2/places?categories=religion.place_of_worship.christianity&apiKey=990f45fdbdd647e4aafbcc204a461b4f&filter=place:{place_id}&limit={limit}&offset={offset}'
            r = requests.get(url)
            print("Url:", url)
            print("Status code:", r.status_code)
            print("Text:", r.text)
            r.raise_for_status()
            data = r.json().get("features", [])
            if not data:
                print('No data')
                break
            all_places.extend([f["properties"] for f in data])
            offset += limit
            if offset >= maxlimit:
                print('Max limit reached')
                break
            time.sleep(0.3)
            print('Total places:', len(all_places))
        write(all_places)
        return all_places
    except Exception as e:
        print(f"Caught an exception: {e}")
        write(all_places)


if __name__ == "__main__":
    main()
    print('done')

