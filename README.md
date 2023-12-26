As of December 26th 2023, all upload attempts (for LPF_Conflated.geojson and sample.geojson to the WHG website) fail without any warnings or errors.

Most recent changes:

Each description is now an individual element in a 'descriptions' list.
Removed "Number of Battles".

NOTE:

In the original data, there are edge cases where the data is not formatted consistently, such as the entry for the 2003 Baghdad Conflict (each underscore is an empty space):

Baghdad	Historical Conflict Event Dataset	2003 ['Gulf War_________________________War']

Another example would be the entry for the 1939 conflict in Albania:

Albania	Historical Conflict Event Dataset	1939 ['World War II', 'World War II']

I attempted to address unique edge cases, but unfortunately there are more than I am aware of, as I am constantly discovering new ones.
