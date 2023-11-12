import json

def validate_lpf(json_data):
    violations = []
    
    # Root level checks
    if "type" not in json_data or json_data["type"] != "FeatureCollection":
        violations.append("Root 'type' must be 'FeatureCollection'")
    if "@context" not in json_data:
        violations.append("'@context' is required.")
    if "features" not in json_data:
        violations.append("'features' element is missing.")
    
    # Check each feature
    for feature in json_data["features"]:
        if "@id" not in feature:
            violations.append("Feature missing '@id'.")
        if "type" not in feature or feature["type"] != "Feature":
            violations.append("Feature 'type' must be 'Feature'.")
        
        # Properties checks
        if "properties" not in feature:
            violations.append("Feature missing 'properties'.")
        else:
            if "title" not in feature["properties"]:
                violations.append("Properties missing 'title'.")
            if "ccodes" in feature["properties"]:
                if not isinstance(feature["properties"]["ccodes"], list):
                    violations.append("'ccodes' should be a list.")
        
        # When checks
        if "when" not in feature:
            violations.append("Feature missing 'when'.")
        else:
            if "timespans" not in feature["when"]:
                violations.append("'when' missing 'timespans'.")
        
        # Geometry checks
        if "geometry" not in feature:
            violations.append("Feature missing 'geometry'.")
        
        # Names checks
        if "names" not in feature:
            violations.append("Feature missing 'names'.")
        else:
            if not any("citations" in name for name in feature["names"]):
                violations.append("Feature ID " + feature["@id"] + " missing citations.")
    
    return violations

with open("LPF_Battles.json", "r") as file:
    data = json.load(file)
    issues = validate_lpf(data)
    
    if issues:
        print("Found violations:")
        for issue in issues:
            print("-", issue)
    else:
        print("No violations found.")


