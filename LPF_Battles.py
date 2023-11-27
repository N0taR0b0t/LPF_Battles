import csv
import json

def process_csv_to_json(csv_file_path):
    features = []

    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            (
                id, title, _, year, _, _, country_code, _,
                _, identifier, _, longitude, latitude, *rest
            ) = row

            # Extract description from the rest of the row
            description = rest[-3] if len(rest) >= 3 else ''

            # Convert longitude and latitude to float if they are not empty
            coordinates = [float(longitude), float(latitude)] if longitude and latitude else None

            # Create the feature object
            feature = {
                "@id": [id],
                "type": "Feature",
                "properties": {
                    "title": title,
                    "ccodes": [country_code] if country_code else []
                },
                "when": {
                    "timespans": [
                        {
                            "start": {
                                "in": year
                            }
                        }
                    ]
                },
                "types": [
                    {
                        "identifier": identifier,
                        "label": "battlefield"
                    }
                ],
                "names": [
                    {
                        "toponym": title
                    }
                ],
                "geometry": {
                    "type": "Point",
                    "coordinates": coordinates
                },
                "descriptions": [
                    {
                        "value": description
                    }
                ]
            }

            features.append(feature)

    # Creating the final JSON structure
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
