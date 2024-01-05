import re
import csv
import json
import logging
import math

# Set up logging
logging.basicConfig(filename='lpf_processing.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def unquote_country_codes(json_file_path):
    # Read the content of the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace quoted country codes in the 'ccodes' array with unquoted ones and ensure the closing bracket is on a new line
    # This regular expression looks for 'ccodes' arrays and handles newlines correctly
    content = re.sub(r'("ccodes": \[\s*)"([A-Z]{2})"\s*\n\s*\]', r'\1\2\n            ]', content, flags=re.MULTILINE)

    # Write the modified content back to the file
    with open(json_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def normalize_title(title):
    # Regular expression to match parentheses with three or fewer characters inside
    pattern = r'\s*\(\w{1,3}\)'

    # Remove matching patterns from the title
    normalized_title = re.sub(pattern, '', title).strip()

    return normalized_title

def clean_description(description):
    return description.replace("[", "").replace("]", "").replace("'", "")

# Function to calculate distance using Haversine formula
def haversine(coord1, coord2):
    R = 6371.0  # Earth radius in kilometers

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# Function to check if two sets of coordinates are close to each other
def are_coordinates_close(coord1, coord2, threshold=0.65):  # Threshold unit is kilometers
    if coord1 is None or coord2 is None:
        return False
    return haversine(coord1, coord2) <= threshold

# Function to check the validity of coordinates
def is_valid_coord(longitude, latitude):
    try:
        longitude = float(longitude)
        latitude = float(latitude)
        return -180 <= longitude <= 180 and -90 <= latitude <= 90
    except ValueError:
        return False

def process_csv_conflate_duplicates(csv_file_path):
    conflated_events = {}

    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            id = row['id']
            original_title = row['title']
            normalized_title = normalize_title(original_title)
            year = row['start']
            country_code = row['ccodes']
            identifier = row['aat_types']
            longitude = row['lon']
            latitude = row['lat']
            description = row['description'] if 'description' in row and row['description'] else "No description provided"
            cleaned_description = clean_description(description)
            description_with_year = f"{cleaned_description} ({year})"
            description_with_year = re.sub(r' {2,}', ' ', description_with_year)  # Replace multiple spaces with a single space

            if not is_valid_coord(longitude, latitude):
                logging.warning(f"Missing or invalid coordinates for {normalized_title}. Using placeholder.")
                coordinates = [0.0, 0.0]
            else:
                coordinates = [float(longitude), float(latitude)]

            if normalized_title not in conflated_events:
                conflated_events[normalized_title] = {
                    '@id': id,
                    'type': 'Feature',
                    'properties': {'title': normalized_title, 'ccodes': [country_code]},
                    'when': {'timespans': [{'start': {'in': year}}]},
                    'names': [{'toponym': normalized_title}],
                    'types': [{'identifier': identifier, 'label': 'battlefield'}],
                    'geometry': {'type': 'Point', 'coordinates': coordinates},
                    'descriptions': [{'value': description_with_year, 'lang': 'en'}]
                }
            else:
                event = conflated_events[normalized_title]
                new_timespan = {'start': {'in': year}}
                if new_timespan not in event['when']['timespans']:
                    event['when']['timespans'].append(new_timespan)

                if description_with_year not in [desc['value'] for desc in event['descriptions']]:
                    event['descriptions'].append({'value': description_with_year, 'lang': 'en'})

    features = [event for event in conflated_events.values()]
    lpf_data = {
        'type': 'FeatureCollection',
        '@context': 'https://linkedpasts.org/assets/linkedplaces-context-v1.jsonld',
        'features': features
    }

    return lpf_data

# Main execution block
def main():
    csv_file_path = 'Original.csv'
    lpf_json_data = process_csv_conflate_duplicates(csv_file_path)

    output_json_file_path = 'LPF_Conflated.geojson'
    with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(lpf_json_data, json_file, indent=4)

    # Call the unquote_country_codes function after writing the JSON file
    unquote_country_codes(output_json_file_path)

    logging.info("Processed data saved to: " + output_json_file_path)

if __name__ == "__main__":
    main()