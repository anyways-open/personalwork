import json

# Read in init data


parsed_init = json.loads(open('init.json','r').read())
geodata_file = parsed_init['geodata_file']
parsed_geodata = json.loads(open(geodata_file,'r').read())

# read data from geodata_file
output="stop_id,stop_name,stop_lat,stop_lon"+"\n"
stop_id=1
test_josm = parsed_geodata['generator']
for item in parsed_geodata['features']:
    if item.get("properties"):
        output+=str(stop_id)+","
        output+=str(item.get('properties').get("name"))+","
        output+=str(item.get('geometry').get("coordinates")[1])+","
        output+=str(item.get('geometry').get("coordinates")[0])
        output+="\n"
        stop_id+=1
        
#create file "Stop-times"

   
# opens an geoJSON file to write the output to
outFileHandle = open("output.geojson",'w')
outFileHandle.write(output)
outFileHandle.close()
