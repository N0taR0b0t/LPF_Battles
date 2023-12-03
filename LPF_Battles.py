import csv
import json

def are_coordinates_close(coord1, coord2, threshold=0.01):
    """Check if two coordinates are within a certain threshold."""
    if coord1 is None or coord2 is None:
        return False
    return abs(coord1[0] - coord2[0]) <= threshold and abs(coord1[1] - coord2[1]) <= threshold

def process_csv_conflate_duplicates(csv_file_path, threshold=0.01):
    # List to store all events
    events = []

    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            (
                id, title, _, start_year, _, _, country_code, _,
                _, identifier, _, longitude, latitude, *rest
            ) = row

            description = rest[-3].strip("[]' ") if len(rest) >= 3 else ''
            coordinates = (float(longitude), float(latitude)) if longitude and latitude else None

            event = {
                "id": id,
                "title": title,
                "country_code": country_code,
                "identifier": identifier,
                "start": start_year,
                "description": description,
                "coordinates": coordinates
            }
            events.append(event)

    # Creating the final JSON structure
    features = []
    processed = set()

    for event in events:
        if event["id"] in processed:
            continue

        # Find similar events based on title and proximity
        similar_events = [e for e in events if e["id"] != event["id"] and e["title"] == event["title"] and are_coordinates_close(e["coordinates"], event["coordinates"], threshold)]
        for e in similar_events:
            processed.add(e["id"])

        all_events = [event] + similar_events
        start_years = "; ".join(sorted(set(e["start"] for e in all_events)))
        descriptions = "; ".join(set(e["description"] for e in all_events))
        battle_count = len(all_events)

        feature = {
            "@id": event["id"],
            "type": "Feature",
            "properties": {
                "title": event["title"],
                "ccodes": [event["country_code"]] if event["country_code"] else []
            },
            "when": {
                "timespans": [{"start": {"in": start_years}}]
            },
            "types": [
                {
                    "identifier": event["identifier"],
                    "label": "battlefield"
                }
            ],
            "names": [{"toponym": event["title"]}],
            "geometry": {
                "type": "Point",
                "coordinates": event["coordinates"]
            },
            "descriptions": [{"value": f"{descriptions} (Number of battles: {battle_count})"}]
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
lpf_json_data = process_csv_conflate_duplicates(csv_file_path)

# Save the processed data to a new JSON file
output_json_file_path = 'Processed_LPF_Conflated.json'
with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(lpf_json_data, json_file, indent=4)

print("Processed data saved to:", output_json_file_path)
