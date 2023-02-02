#ifndef sensorsStates_h
#define sensorsStates_h

/* GLOBAL VALUES OF THE SENSORS:
0 - PM10;
1 - TEMPERATURE;
2 - HUMIDITY;
3 - OZONE;
4 - BENZENE;
5 - AMMONIA;
6 - ALDEHYDES;
7 - GPS;
*/

bool sensorsActiveFlags[] = {true,true,false,false,true,true,true,true}; //This arrays describes for each sensor if we shall read it during read_from_sensor() execution --> true (we read the i sensor) ; false (we skip the reading process for the i sensor)
String sensorsNames[] = {"PM10","Temperature","Humidity","Ozone","Benzene","Ammonia","Aldehydes","GPS"};
String sensorsUnits[] = {"°C","%","pcs/0.01cf","ppm","ppm","ppm","ppm","°"};
String sensorsValues[] = {"-","-","-","-","-","-","-","-"}; //this may substitute every statoX variable. it contains for each sensor the value read.


String getSensInfos(int k){
    String result = sensorsNames[k] + ":" + sensorsValues[k] +"|";
    return result;
}

#endif
