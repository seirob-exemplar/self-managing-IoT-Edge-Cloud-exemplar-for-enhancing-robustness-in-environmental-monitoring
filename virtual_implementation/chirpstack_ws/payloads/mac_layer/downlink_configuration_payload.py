import json

'''
0 - PM10;
1 - TEMPERATURE;
2 - HUMIDITY;
3 - OZONE; impiega molto a fare la calibrazione quindi metto 0
4 - BENZENE;
5 - AMMONIA;
6 - ALDEHYDES;
7 - GPS;
8 - timetosend
9 - timetoreceive
example of msg received: "1|1|1|0|1|1|1|1|20000|50000" -> 1=true (I want to read the sensor i) 0=false (I don't care about sensor i)
'''

class DownlinkConfigurationPayload:
    def __init__(self, timestosend=0, timetoreceive=0):
        self.PM10 = False
        self.temperature = False
        self.humidity = False
        self.ozone = False
        self.benzene = False
        self.ammonia = False
        self.aldehydes = False
        self.GPS = False
        self.timetosend = timestosend
        self.timetoreceive = timetoreceive

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
