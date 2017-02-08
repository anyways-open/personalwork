#import json

# Read in init data


#parsed_init = json.loads(open("init.json", 'rb'))
#geodata_file = parsed_init["geodata_file"]
#parsed_geodata = json.loads(open(geodata_file, 'rb'))

# read data from geodata_file

#test_josm = parsed_json['generator']

#create file "Stop-times"

output="test_josm" 
    
# opens an geoJSON file to write the output to
outFileHandle = open("output.geojson", "w")
outFileHandle.write(output)
outFileHandle.close()