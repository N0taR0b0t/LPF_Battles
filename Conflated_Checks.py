import json

def check_for_duplicates(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    features = data['features']
    place_names = {}
    duplicate_issues = []

    for feature in features:
        # Extracting the primary title
        title = feature['properties']['title']

        # Check if the title already exists
        if title in place_names:
            duplicate_issues.append(f"Duplicate title found: {title}")
        else:
            place_names[title] = True

    return duplicate_issues

# Path to the JSON file
json_file_path = 'Processed_LPF_Conflated.json'

# Checking for duplicates
issues = check_for_duplicates(json_file_path)

if issues:
    print("Issues found:")
    for issue in issues:
        print(issue)
else:
    print("No duplicate issues found.")
