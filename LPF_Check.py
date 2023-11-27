import json

def validate_lpf(json_data):
    violations = []
    titles_seen = set()  # To track titles for duplicate check
    
    if "type" not in json_data or json_data["type"] != "FeatureCollection":
        violations.append("Root 'type' must be 'FeatureCollection'")
    
    if "@context" not in json_data:
        violations.append("'@context' is required.")
    
    if "features" not in json_data:
        violations.append("'features' element is missing.")
    else:
        for feature in json_data["features"]:
            if "@id" not in feature:
                violations.append("Feature missing '@id'.")
            if "type" not in feature or feature["type"] != "Feature":
                violations.append("Feature 'type' must be 'Feature'.")
            if "properties" not in feature:
                violations.append("Feature missing 'properties'.")
            else:
                if "title" not in feature["properties"]:
                    violations.append("Properties missing 'title'.")
                else:
                    # Check for duplicate titles
                    title = feature["properties"]["title"]
                    if title in titles_seen:
                        violations.append(f"Duplicate title found: '{title}'")
                    else:
                        titles_seen.add(title)

                if "ccodes" in feature["properties"]:
                    if not isinstance(feature["properties"]["ccodes"], list):
                        violations.append("'ccodes' should be a list.")
            if "when" not in feature:
                violations.append("Feature missing 'when'.")
            else:
                if "timespans" not in feature["when"]:
                    violations.append("'when' missing 'timespans'.")
            if "geometry" not in feature:
                violations.append("Feature missing 'geometry'.")
            if "names" not in feature:
                violations.append("Feature missing 'names'.")
            else:
                if not any("citations" in name for name in feature["names"]):
                    violations.append("At least one name must have a citation.")
    
    return violations

# You would replace "Processed_LPF.json" with the actual path of your JSON file.
with open("Processed_LPF.json", "r") as file:
    data = json.load(file)
    issues = validate_lpf(data)
    
    issue_count = len(issues)
    if issues:
        if issue_count > 20:
            print(f"Found {issue_count} violations.")
        else:
            print("Found violations:")
            for issue in issues:
                print("-", issue)
    else:
        print("No violations found.")
