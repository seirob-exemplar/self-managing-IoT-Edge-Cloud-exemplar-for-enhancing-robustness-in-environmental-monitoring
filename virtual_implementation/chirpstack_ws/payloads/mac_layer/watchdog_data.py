import base64
import json

from utils.payload_util import get_json_from_object

'''
0 - PM10;
1 - TEMPERATURE;
2 - HUMIDITY;
3 - OZONE;
4 - BENZENE;
5 - AMMONIA;
6 - ALDEHYDES;
7 - GPS; 2 valori -> latitude & longitude'''
class WatchdogData:

    def __init__(self):
        self.PM10 = None
        self.temperature = None
        self.humidity = None
        self.ozone = None
        self.benzene = None
        self.ammonia = None
        self.aldehydes = None
        self.GPS = None
        self.battery = None

    def encode_data(self):
        json_data = get_json_from_object(self)
        json_string_data = json.dumps(json_data)
        json_string_encoded_data = json_string_data.encode()
        b64_encoded_data = base64.b64encode(json_string_encoded_data)  # array di byte in base64
        return b64_encoded_data.decode()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
