import requests

def get_place_name(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "extratags": 1,
        "limit": 1
    }
    headers = {
        "User-Agent": "church-map-script"
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    results = response.json()
    if results:
        place = results[0]
        # Try to get business/church name from extra tags or address
        tags = place.get("extratags", {})
        name = tags.get("name") or tags.get("operator")
        # Try to get from address fields
        if not name:
            addr = place.get("address", {})
            name = addr.get("church") or addr.get("place_of_worship") or addr.get("building") or addr.get("amenity")
        # Fallback to display_name only if it looks like a business/church name
        if not name:
            display_name = place.get("display_name", "")
            # Heuristic: if display_name contains 'Church', 'Temple', 'Business', etc.
            for keyword in ["Church", "Temple", "Business", "Chapel", "Synagogue", "Mosque", "Cathedral", "Meetinghouse", "Stake Center", "Institute", "Seminary"]:
                if keyword.lower() in display_name.lower():
                    name = display_name
                    break
        return name or "No result found"
    else:
        return "No result found"

if __name__ == "__main__":
    address = input("Enter address: ")
    print("Place name:", get_place_name(address))
