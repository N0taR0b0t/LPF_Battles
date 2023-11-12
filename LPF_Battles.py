import json
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance in miles between two points on the earth"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of Earth in miles
    return c * r

def combine_features(features):
    combined_features = {}

    for feature in features:
        title = feature['properties']['title']
        coordinates = feature['geometry']['coordinates'] if 'geometry' in feature else None

        if title not in combined_features:
            combined_features[title] = feature
        else:
            existing_feature = combined_features[title]
            existing_coordinates = existing_feature['geometry']['coordinates'] if 'geometry' in existing_feature else None

            if coordinates and existing_coordinates:
                distance = haversine(coordinates[0], coordinates[1], existing_coordinates[0], existing_coordinates[1])
                if distance <= 100:
                    # Combine features
                    for key in feature:
                        if key in existing_feature:
                            if isinstance(existing_feature[key], list):
                                # Special handling for list of dictionaries
                                if existing_feature[key] and isinstance(existing_feature[key][0], dict):
                                    existing_feature[key].extend(x for x in feature[key] if x not in existing_feature[key])
                                else:
                                    existing_feature[key] = list(set(existing_feature[key] + feature[key]))  # Merge lists without duplicates
                            elif isinstance(existing_feature[key], dict):
                                for sub_key in feature[key]:
                                    if sub_key in existing_feature[key]:
                                        if isinstance(existing_feature[key][sub_key], list):
                                            # Special handling for list of dictionaries
                                            if existing_feature[key][sub_key] and isinstance(existing_feature[key][sub_key][0], dict):
                                                existing_feature[key][sub_key].extend(x for x in feature[key][sub_key] if x not in existing_feature[key][sub_key])
                                            else:
                                                existing_feature[key][sub_key] = list(set(existing_feature[key][sub_key] + feature[key][sub_key]))
                                        else:
                                            existing_feature[key][sub_key] = feature[key][sub_key]
                                    else:
                                        existing_feature[key][sub_key] = feature[key][sub_key]
                        else:
                            existing_feature[key] = feature[key]

    return list(combined_features.values())


# Read LPF JSON file
with open('LPF_Battles.json', 'r', encoding='utf-8') as file:
    lpf_data = json.load(file)

# Combine features
combined_features = combine_features(lpf_data['features'])

# Update LPF data
lpf_data['features'] = combined_features

# Save combined data to new JSON file
with open('LPF_Battles.json', 'w', encoding='utf-8') as json_file:
    json.dump(lpf_data, json_file, indent=4)

print(f"Combined {len(lpf_data['features'])} features")
