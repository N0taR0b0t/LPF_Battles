As of December 23rd 2023, neither LPF_Conflated.geojson nor sample.geojson were able to be uploaded to the WHG website.

All upload attempts fail with no error message.

Work in Progress/Will be done soon:

Descriptions Field: Modify the script to ensure that each description is an individual element in a 'descriptions' list. This list should be separate from the 'properties' dictionary.

Remove "Number of Battles": The phrase "- (Number of battles: X)" should be removed from the description.

NOTE:

In the original data, there are edge cases where the data is not formatted consistently, such as the entry for the 2003 Baghdad Conflict (each underscore is an empty space):

Baghdad	Historical Conflict Event Dataset	2003				['Gulf War_________________________War']
