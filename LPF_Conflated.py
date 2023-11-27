import csv
import json

def process_csv_to_json(csv_file_path):
    location_dict = {}  # Dictionary to track locations and their events

    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            (
                id, title, _, year, _, _, country_code, _,
                _, identifier, _, longitude, latitude, *rest
            ) = row

            description = rest[-3] if len(rest) >= 3 else ''
            coordinates = [float(longitude), float(latitude)] if longitude and latitude else None

            # Create a unique key for each location based on coordinates
            location_key = f"{longitude},{latitude}"
            event = {
                "id": id,
                "start": {"in": year},
                "title": title,
                "description": description,
                "identifier": identifier,
                "country_code": country_code
            }

            # Conflate events at the same location
            if location_key in location_dict:
                location_dict[location_key]["events"].append(event)
            else:
                location_dict[location_key] = {
                    "coordinates": coordinates,
                    "events": [event],
                    "titles": set()  # Initialize a set to track unique titles
                }

    # Creating the final JSON structure
    features = []
    for location_key, location in location_dict.items():
        # Populate the set of unique titles for this location
        unique_titles = {event["title"] for event in location["events"]}

        feature = {
            "@id": location["events"][0]["id"],
            "type": "Feature",
            "properties": {
                "title": location["events"][0]["title"],
                "ccodes": [location["events"][0]["country_code"]] if location["events"][0]["country_code"] else []
            },
            "when": {
                "timespans": [{"start": event["start"]} for event in location["events"]]
            },
            "types": [
                {
                    "identifier": location["events"][0]["identifier"],
                    "label": "battlefield"
                }
            ],
            "names": [{"toponym": title} for title in unique_titles],
            "geometry": {
                "type": "Point",
                "coordinates": location["coordinates"]
            },
            "descriptions": [{"value": event["description"]} for event in location["events"]]
        }
        features.append(feature)

    lpf_data = {
        "type": "FeatureCollection",
        "@context": "https://linkedpasts.org/assets/linkedplaces-context-v1.jsonld",
        "features": features
    }

    return lpf_data

# Process the CSV file and convert it to JSON format
csv_file_path = 'Original.csv'
lpf_json_data = process_csv_to_json(csv_file_path)

# Save the processed data to a new JSON file
output_json_file_path = 'Processed_LPF.json'
with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(lpf_json_data, json_file, indent=4)

output_json_file_path
