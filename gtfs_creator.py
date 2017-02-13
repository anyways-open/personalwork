import json
import time
import math
import datetime

# Read in init data


parsed_init = json.loads(open('init.json','r').read())
geodata_file = parsed_init['geodata_file']
parsed_geodata = json.loads(open(geodata_file,'r').read())

# read data from geodata_file for stops
outputStops="stop_id,stop_name,stop_lat,stop_lon"+"\n"
stop_id=1
test_josm = parsed_geodata['generator']
stopList=[]
for item in parsed_geodata['features']:
    if item.get("properties"):
        outputStops+=str(stop_id)+","
        outputStops+=str(item.get('properties').get("name"))+","
        outputStops+=str(item.get('geometry').get("coordinates")[1])+","
        outputStops+=str(item.get('geometry').get("coordinates")[0])
        outputStops+="\n"
        stopList+=[[str(item.get('properties').get("name")), item.get('geometry').get("coordinates")[1], item.get('geometry').get("coordinates")[0], stop_id]]
        stop_id+=1
# read geo for coordinates and create array with stops in right order

outputStoptimes="trip_id,arrival_time,departure_time,stop_id,stop_sequence"+"\n"

# parse the coördinates list from the line - only one line can be handeled!

for item in parsed_geodata['features']:
    if item.get("geometry").get("type")=="LineString":
        parsed_line=item.get("geometry").get("coordinates")

# compare the coordinates from the linestring with the stops, and order them from start to finish. Result is a list of [id, sequence] pairs that can be input in the final stop_times.txt
count=1
stopTimesList=[]

for pair in parsed_line:
    lineCoordx=str(pair[1])
    lineCoordy=str(pair[0])
    for stop in stopList:
        if str(stop[1])==lineCoordx and str(stop[2])==lineCoordy:
            stopTimesList+=[[count,stop[1],stop[2],stop[0],stop[3]]]
            count+=1


# now we need to get the time between two stops as the distance traveled devided by the speed of the line, given in the init file. we store that in a list travelTimes[]

speed=parsed_init['speed']/3.6
#speed converted in m/s from the speed in the init file in km/h
travelTimes=[]
for i in range(0,count-2):

    lat1, lng1 = math.radians(stopTimesList[i][1]), math.radians(stopTimesList[i][2])
    lat2, lng2 = math.radians(stopTimesList[i+1][1]), math.radians(stopTimesList[i+1][2])

    distance=math.acos((math.sin(lat1)*math.sin(lat2))+(math.cos(lat1)*math.cos(lat2)*math.cos(lng2-lng1)))*6371000
    travelTimes+=[distance/speed] #travelTimes in seconds, distance in meters

# read data from geodata_file for routes from one line only: 1 is up, 2 is down
outputRoutes="route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color"+"\n"
outputRoutes+="1,%s,X01,opgaande lijn,,1,,e52424,FFFFFF" % (parsed_init['Agency'])+"\n"
outputRoutes+="2,%s,X02,neergaande lijn,,1,,4424e5,FFFFFF" % (parsed_init['Agency'])+"\n"

# start building trips: determine the number of trips based on start, stop and headway

trips_start=time.strptime(parsed_init['start'],"%H:%M:%S")
trips_end=time.strptime(parsed_init['end'],"%H:%M:%S")
trips_headway=parsed_init['headway']

trips_numberof=int(60*(trips_end[3]-trips_start[3])/trips_headway)

# function to add time values

def addTime(h1, m1, s1, h2, m2, s2):
    s12=s1+s2
    m12=m1+m2
    h12=h1+h2
    s=int(s12%60)
    m=int((m12+s12/60)%60)
    h=int(h12+(m12+(s12/60))/60)
    time_def="%(hour)02d:%(minute)02d:%(second)02d" %{"hour":h,"minute":m,"second":s}
    return (time_def)
       

# trips stop times
for line in ["op","af"]:
    if line=="af":
        travelTimes.reverse()
        stopTimesList.reverse()

    busstop_time=parsed_init["busstop_time"]
    starttime=time.strptime(parsed_init['start'],"%H:%M:%S")

    for i in range(1,trips_numberof):
        trip_accum_time=time.strptime("00:00:00","%H:%M:%S")
        n=0
        outputStoptimes+=line+"%s"%(str(i))+"," #trip_id
        new_stoptime=addTime(starttime[3],starttime[4],starttime[5],0,0,0)
        outputStoptimes+=new_stoptime+"," #arrival_time
        starttime=time.strptime(new_stoptime,"%H:%M:%S")
        new_stoptime=addTime(starttime[3],starttime[4],starttime[5],0,0,busstop_time)
        outputStoptimes+=new_stoptime+"," #departure_time
        outputStoptimes+=str(stopTimesList[n][4])+"," #stop_id
        outputStoptimes+=str(n+1)+"\n" #sequence
        trip_accum_time=time.strptime(addTime(trip_accum_time[3],trip_accum_time[4],trip_accum_time[5],0,0,busstop_time),"%H:%M:%S")
        for j in travelTimes:
            # add travel time
            tt_s=int(j%60)
            tt_m=int((j/60)%60)
            tt_h=int(j/3600)
            trip_accum_time=time.strptime(addTime(trip_accum_time[3],trip_accum_time[4],trip_accum_time[5],tt_h,tt_m,tt_s),"%H:%M:%S")
            outputStoptimes+=line+"%s"%(str(i))+"," #trip_id
            new_stoptime=addTime(starttime[3],starttime[4],starttime[5],trip_accum_time[3],trip_accum_time[4],trip_accum_time[5])
            outputStoptimes+=new_stoptime+"," #arrival_time
            starttime=time.strptime(new_stoptime,"%H:%M:%S")
            new_stoptime=addTime(starttime[3],starttime[4],starttime[5],0,0,busstop_time)
            outputStoptimes+=new_stoptime+"," #departure_time
            outputStoptimes+=str(stopTimesList[n+1][4])+"," #stop_id
            outputStoptimes+=str(n+2)+"\n" #sequence
            n+=1
        starttime=time.strptime(parsed_init['start'],"%H:%M:%S")
        starttime=time.strptime(addTime(starttime[3],starttime[4],starttime[5],0,trips_headway*i,0),"%H:%M:%S")
    

# read data from geodata_file from line, and sort from start to finish.

outputTrips="route_id,service_id,trip_id,trip_headsign,shape_id"+"\n"
for i in range(1,trips_numberof):
    outputTrips+="1,FULLW,op%s,opgaande lijn,"%(str(i))+"\n"
for i in range(1,trips_numberof):
    outputTrips+="2,FULLW,neer%s,terugkomende lijn,"%(str(i))+"\n"
    
   
# opens stops file to write the output to
outFileHandle = open("stops.txt",'w')
outFileHandle.write(outputStops)
outFileHandle.close()

# opens a routes file to write the output to
outFileHandle = open("routes.txt",'w')
outFileHandle.write(outputRoutes)
outFileHandle.close()

# opens a trips file to write the output to
outFileHandle = open("trips.txt",'w')
outFileHandle.write(outputTrips)
outFileHandle.close()

# opens a stop_times file to write the output to
outFileHandle = open("stop_times.txt",'w')
outFileHandle.write(outputStoptimes)
outFileHandle.close()
