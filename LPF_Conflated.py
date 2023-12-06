import csv
import json
import logging

#TODO Kandahar is gone, put it back
#TODO: Fix IDs such that they are integers
#TODO: Possibly convert coordinates to miles, as longitude changes with the curves of the Earth
#Use the proper GIS coordinate system
#Make sure the years go from lowest to greatest and titles matches order
#Add battles year to value description

logging.basicConfig(filename='lpf_processing.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def are_coordinates_close(coord1, coord2, threshold=0.1):
    if coord1 is None or coord2 is None:
        return False
    return abs(coord1[0] - coord2[0]) <= threshold and abs(coord1[1] - coord2[1]) <= threshold

def process_csv_conflate_duplicates(csv_file_path):
    events = []

    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)

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

    conflated_events = {}

    for event in events:
        title = event["title"]
        coordinates = event["coordinates"]

        if title in conflated_events:
            existing_event = conflated_events[title]
            existing_coordinates = existing_event['coordinates']

            if are_coordinates_close(coordinates, existing_coordinates):
                existing_event['timespans'].add(event['start'])
                existing_event['descriptions'].add(event['description'])
                existing_event['battle_count'] += 1
            else:
                modified_title = f"{title}_{coordinates}"
                conflated_events[modified_title] = {
                    'timespans': {event['start']},
                    'descriptions': {event['description']},
                    'battle_count': 1,
                    'country_code': event['country_code'],
                    'identifier': event['identifier'],
                    'coordinates': event['coordinates']
                }

        else:
            conflated_events[title] = {
                'timespans': {event['start']},
                'descriptions': {event['description']},
                'battle_count': 1,
                'country_code': event['country_code'],
                'identifier': event['identifier'],
                'coordinates': event['coordinates']
            }

    features = []
    for title, data in conflated_events.items():
        feature = {
            "@id": title,
            "type": "Feature",
            "properties": {
                "title": title,
                "ccodes": [data['country_code']] if data['country_code'] else []
            },
            "when": {
                "timespans": [{"start": {"in": "; ".join(sorted(data['timespans']))}}]
            },
            "types": [
                {
                    "identifier": data['identifier'],
                    "label": "battlefield"
                }
            ],
            "names": [{"toponym": title}],
            "geometry": {
                "type": "Point",
                "coordinates": data['coordinates']
            },
            "descriptions": [{"value": f"{'; '.join(data['descriptions'])} (Number of battles: {data['battle_count']})"}]
        }
        features.append(feature)

    lpf_data = {
        "type": "FeatureCollection",
        "@context": "https://linkedpasts.org/assets/linkedplaces-context-v1.jsonld",
        "features": features
    }

    return lpf_data

csv_file_path = 'Original.csv'
lpf_json_data = process_csv_conflate_duplicates(csv_file_path)

output_json_file_path = 'Processed_LPF_Conflated.json'
with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(lpf_json_data, json_file, indent=4)

logging.info("Processed data saved to: " + output_json_file_path)
