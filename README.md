GTFS creator

this is a simple GTFS editor that uses a geojson file built in JOSM ot create a set of GTFS files for a line or service. 

Draw a line in JOSM, and define the stops as points on the line with tag 'public_transport'='stop_position' and give the stops a name with the name tag. Example given in repository is "pendel_1.geojson"

Uses a simple "init.json" file to set some parameters.

So far only creation of GTFS "stops" file, more to come...
