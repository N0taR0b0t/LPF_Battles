As of December 23rd 2023, neither LPF_Conflated.geojson nor sample.geojson were able to be uploaded to the WHG website.

All upload attempts fail with no error message.

Newly Implemented Features (but not yet tested for the purpose of quality assurance):

Descriptions Field: Modified the script to ensure that each description is an individual element in a 'descriptions' list.

Removed "Number of Battles": The phrase "- (Number of battles: X)" was removed from the description.

NOTE:

In the original data, there are edge cases where the data is not formatted consistently, such as the entry for the 2003 Baghdad Conflict (each underscore is an empty space):

Baghdad	Historical Conflict Event Dataset	2003 ['Gulf War_________________________War']

Another example would be the entry for the 1939 conflict in Albania:

Albania	Historical Conflict Event Dataset	1939 ['World War II', 'World War II']

I attempted to address unique edge cases, but unfortunately there are more than I am aware of, as I am constantly discovering new ones.
