import json
import csv

# Input and output file paths
input_file = 'first-output.json'
output_file = 'churches.csv'

# Fields to extract
fields = [
    'name', 'address', 'zip_code', 'city', 'phone', 'website', 'denomination'
]

def extract_church_info(church):
    # Name
    name = church.get('name', '')
    # Address (combine housenumber and street)
    housenumber = church.get('housenumber', '') or church.get('datasource', {}).get('raw', {}).get('addr:housenumber', '')
    street = church.get('street', '') or church.get('datasource', {}).get('raw', {}).get('addr:street', '')
    address = f"{housenumber} {street}".strip()
    # Zip code
    zip_code = church.get('postcode', '') or church.get('datasource', {}).get('raw', {}).get('addr:postcode', '')
    # City
    city = church.get('city', '') or church.get('datasource', {}).get('raw', {}).get('addr:city', '')
    # Phone
    phone = church.get('contact', {}).get('phone', '') or church.get('datasource', {}).get('raw', {}).get('phone', '')
    # Website
    website = church.get('website', '') or church.get('datasource', {}).get('raw', {}).get('website', '')
    # Denomination
    denomination = (
        church.get('place_of_worship', {}).get('denomination', '') or
        church.get('datasource', {}).get('raw', {}).get('denomination', '')
    )
    # Categorizer: relabel 'mormon', 'latter_day_saints', 'latter-day_saints', or name contains 'LDS'/'Latter Day' as 'lds'
    name_lower = name.lower()
    if (
        denomination.strip().lower() in ['mormon', 'latter_day_saints', 'latter-day_saints']
        or 'lds' in name_lower
        or 'latter day' in name_lower
        or 'latter-day' in name_lower
    ):
        denomination = 'lds'
    return {
        'name': name,
        'address': address,
        'zip_code': zip_code,
        'city': city,
        'phone': phone,
        'website': website,
        'denomination': denomination
    }

def main():
    with open(input_file, 'r', encoding='utf-8') as f:
        churches = json.load(f)
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for church in churches:
            info = extract_church_info(church)
            writer.writerow(info)

if __name__ == '__main__':
    main()
