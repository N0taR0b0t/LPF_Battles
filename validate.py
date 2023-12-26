import json
import re

class GeoJSONValidationError(Exception):
    pass

def validate_geojson(file_name):
    errors = []
    verbose_output = []

    # Load GeoJSON file
    with open(file_name, 'r') as file:
        data = json.load(file)

    # Define required fields and patterns
    required_feature_fields = ["@id", "type", "properties", "geometry"]
    required_properties_fields = ["title", "ccodes"]
    required_geometry_fields = ["type", "coordinates"]
    coordinates_range = {"longitude": (-180, 180), "latitude": (-90, 90)}

    # Validate each feature
    for index, feature in enumerate(data.get("features", [])):
        verbose_output.append(f"Validating Feature {index + 1}:")

        # Check required fields in feature
        for field in required_feature_fields:
            if field not in feature:
                errors.append({"feature": index + 1, "error": f"Required field missing in feature: {field}"})
                verbose_output.append(f"  Error: Required field missing in feature: {field}")
            else:
                verbose_output.append(f"  OK: {field} field exists")

        # Validate properties
        properties = feature.get("properties", {})
        for field in required_properties_fields:
            if field not in properties:
                errors.append({"feature": index + 1, "error": f"Required field missing in properties: {field}"})
                verbose_output.append(f"  Error: Required field missing in properties: {field}")
            else:
                verbose_output.append(f"  OK: {field} field exists in properties")

        # Validate geometry
        geometry = feature.get("geometry", {})
        for field in required_geometry_fields:
            if field not in geometry:
                errors.append({"feature": index + 1, "error": f"Required field missing in geometry: {field}"})
                verbose_output.append(f"  Error: Required field missing in geometry: {field}")
            else:
                verbose_output.append(f"  OK: {field} field exists in geometry")

        if "coordinates" in geometry:
            lon, lat = geometry["coordinates"]
            if not (coordinates_range["longitude"][0] <= lon <= coordinates_range["longitude"][1]):
                errors.append({"feature": index + 1, "error": "Longitude out of range"})
                verbose_output.append("  Error: Longitude out of range")
            else:
                verbose_output.append("  OK: Longitude within range")

            if not (coordinates_range["latitude"][0] <= lat <= coordinates_range["latitude"][1]):
                errors.append({"feature": index + 1, "error": "Latitude out of range"})
                verbose_output.append("  Error: Latitude out of range")
            else:
                verbose_output.append("  OK: Latitude within range")

        # Additional checks for other fields like 'when', 'names', 'types', 'descriptions' can be added similarly...

    # Raise exception if there are errors
    if errors:
        raise GeoJSONValidationError("\n".join(verbose_output) + "\n\nValidation errors found.")

    return "\n".join(verbose_output) + "\n\nValidation successful"

# Usage example
try:
    result = validate_geojson("LPF_Conflated.geojson")
    print(result)
except GeoJSONValidationError as e:
    print(str(e))
