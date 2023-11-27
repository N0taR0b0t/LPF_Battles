import json
from collections import Counter

def read_json_and_find_duplicates(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    titles = []
    for feature in data['features']:
        if 'title' in feature['properties']:
            titles.append(feature['properties']['title'])
        else:
            # Warning for missing 'title'
            print(f"Warning: Missing 'title' in feature with ID {feature.get('@id', 'Unknown')}")

    # Counting occurrences of each title
    title_counts = Counter(titles)

    # Filtering for non-unique titles
    non_unique_titles = {title: count for title, count in title_counts.items() if count > 1}

    return non_unique_titles

# Path to the JSON file
json_file_path = 'Processed_LPF.json'

# Find and display non-unique titles
duplicates = read_json_and_find_duplicates(json_file_path)
for title, count in duplicates.items():
    print(f"'{title}' appears {count} times")
