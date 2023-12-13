import csv
import json
import logging
import math

# Set up logging
logging.basicConfig(filename='lpf_processing.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
def are_coordinates_close(coord1, coord2, threshold=1.1):  # Threshold in kilometers (0.7 miles)
    if coord1 is None or coord2 is None:
        return False
    distance = haversine(coord1, coord2)
    return distance <= threshold

# Function to check the validity of coordinates
def is_valid_coord(longitude, latitude):
    try:
        longitude = float(longitude)
        latitude = float(latitude)
        return -180 <= longitude <= 180 and -90 <= latitude <= 90
    except ValueError:
        return False

# Function to process the CSV and create JSON with conflation of duplicates
def process_csv_conflate_duplicates(csv_file_path):
    conflated_events = {}

    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            id = row['id']
            title = row['title']
            year = row['start']
            country_code = row['ccodes']
            identifier = row['aat_types']
            longitude = row['lon']
            latitude = row['lat']
            description = row['description'] if row['description'] else "No description provided"

            if is_valid_coord(longitude, latitude):
                coordinates = (float(longitude), float(latitude))
                year_description = f"{description} ({year})"
            else:
                coordinates = None
                logging.warning(f"Missing or invalid coordinates for {title}. Using placeholder.")
                # Include title in the description for entries with missing coordinates
                year_description = f"{title}: {description} ({year})"

            if title not in conflated_events:
                initial_battle_count = 0
                if coordinates is None:
                    initial_battle_count = 1

                conflated_events[title] = {
                    'id': id,
                    'timespans': [],
                    'descriptions': [],
                    'battle_count': initial_battle_count,
                    'country_code': country_code,
                    'identifier': identifier,
                    'coordinates': coordinates,
                    'toponyms': [title]
                }

            event = conflated_events[title]
            if coordinates is not None and not any(coord == coordinates for coord in event['coordinates']):
                event['timespans'].append(year)
                event['descriptions'].append(year_description)
                event['battle_count'] += 1

            # For entries with null coordinates, always add the description
            if coordinates is None:
                event['descriptions'].append(year_description)

    # Sort timespans chronologically and format descriptions
    for title, data in conflated_events.items():
        data['timespans'].sort()
        data['descriptions'] = "; ".join(data['descriptions']) + " -" + f" (Number of battles: {data['battle_count']})"

    # Creating the final JSON structure
    features = []
    for title, data in conflated_events.items():
        feature = {
            "@id": data['id'],
            "type": "Feature",
            "properties": {
                "title": title,
                "ccodes": [data['country_code']] if data['country_code'] else []
            },
            "when": {
                "timespans": [{"start": {"in": "; ".join(data['timespans'])}}]
            },
            "types": [
                {
                    "identifier": data['identifier'],
                    "label": "battlefield"
                }
            ],
            "names": [{"toponym": toponym} for toponym in data['toponyms']],
            "geometry": {
                "type": "Point",
                "coordinates": data['coordinates']
            },
            "descriptions": [{"value": data['descriptions']}]
        }
        features.append(feature)

    lpf_data = {
        "type": "FeatureCollection",
        "@context": "https://linkedpasts.org/assets/linkedplaces-context-v1.jsonld",
        "features": features
    }

    return lpf_data

# Main execution block
def main():
    csv_file_path = 'Original.csv'
    lpf_json_data = process_csv_conflate_duplicates(csv_file_path)

    output_json_file_path = 'LPF_Conflated.geojson'
    with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(lpf_json_data, json_file, indent=4)

    logging.info("Processed data saved to: " + output_json_file_path)

if __name__ == "__main__":
    main()
