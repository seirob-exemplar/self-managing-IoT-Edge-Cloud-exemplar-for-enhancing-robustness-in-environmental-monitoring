from datetime import datetime
import time
import json
import base64
import random
from typing import TypeVar

import logger
writeLog = logger.getLogger("appserver.log")

from paho.mqtt.client import Client

from enums.working_state_enum import WorkingStateEnum
from payloads.appserver.down_command_payload import DownCommandPayload
from payloads.appserver.ping_payload import PingPayload
from utils.app_server_utils import get_watchdog_app_server, get_watchdog_configuration
from utils.payload_util import get_json_from_object
from utils.api_utils import enqueue_device_downlink
from appserver.gateway_appserver import GatewayAppServer
from appserver.watchdog_appserver import WatchdogAppServer
from payloads.mac_layer.downlink_configuration_payload import DownlinkConfigurationPayload
from enums.watchdog_battery_config_enum import WatchdogBatteryConfigEnum

T = TypeVar('T')


class AppServer:
    # Topics
    # Subscribe topics
    join_topic =   "application/%s/device/%s/event/join"
    up_topic =     "application/%s/device/%s/event/up"
    
    ping_topic =     "eu868/gateway/%s/command/ping"
    echo_topic =     "eu868/gateway/%s/event/echo"
    silentWD_topic = "eu868/gateway/%s/silent/watchdog"

    # Timeout
    gateway_timout = 60000
    MIN_TIME_TO_SEND = 20000 # MAX 200.000 
    MIN_TIME_TO_RECEIVE = 40000 # MAX 200.000

    sensors = ["pm10", "temperature","humidity","ozone","benzene","ammonia","aldehydes","latitude", "longitude", "battery"]

    def __init__(self, broker="", port=None, id_application="", application_name="", ip="localhost",
                 app_server_app=None):
        self.broker = broker
        self.port = port
        self.ip = ip
        self.client = None
        self.client_id = "loraappserver" + str(id_application)
        self.username = "chirpstack_as"
        self.password = ""
        self.id_application = id_application
        self.application_name = application_name
        self.can_sand_data = False
        self.watchdogs:WatchdogAppServer = {} #popolato con le join
        self.gateways:GatewayAppServer = {} # popolato all'inizializzazione
        self.app = app_server_app
        self.fault_detection = True
        self.batteryAdaptation = True

    def start_connection(self):
        try:
            # Set Connecting Client ID
            self.client = Client(client_id=self.client_id)
            self.client.username_pw_set(self.username, self.password)

            # call back functions
            self.client.on_connect = self.on_connect
            self.client.on_connect_fail = self.on_connect_fail
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            self.app.print(f"AppServer connect: {self.client.connect(self.broker, self.port, 60)}")
            writeLog.info(f"AppServer connect: {self.client.connect(self.broker, self.port, 60)}")
            time.sleep(1)
            self.client.loop_start()

            while not self.client.is_connected():
                time.sleep(1)

            self.app.print(f"AppServer connected!")
            writeLog.info(f"AppServer connected!")
            #self.app.print(f"Id-application: {self.id_application}")
        except BaseException as err:
            self.app.print(f"ERROR: AppServer Could not connect to MQTT.")
            self.app.print(f"Unexpected {err=}, {type(err)=}")
            self.close_connection()


    def publish(self, topic, payload: T):
        if not self.client.is_connected():
            self.app.print(f"Appserver not connected!")
            return
        # json conversion
        json_payload = get_json_from_object(payload)
        message = json.dumps(json_payload)

        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            self.app.print(f"AppServer send message to topic {topic}")
            writeLog.info(f"AppServer send message to topic {topic}")
            return

        self.app.print(f"AppServer failed to send message to topic {topic}")
        return

    def subscribe(self, dev_eui):
        join_topic_to_sub = AppServer.join_topic % (self.id_application, dev_eui)
        up_topic_to_sub = AppServer.up_topic % (self.id_application, dev_eui)
        
        self.client.subscribe(join_topic_to_sub)
        self.client.subscribe(up_topic_to_sub)
        

    def subscribe_ping(self, gateway_id):
        echo_topic_to_sub = AppServer.echo_topic % gateway_id
        silent_topic_to_sub = AppServer.silentWD_topic % gateway_id
        self.client.subscribe(echo_topic_to_sub)
        self.client.subscribe(silent_topic_to_sub)
        

    def ping_gateway(self, gateway_id):
        ping_topic = AppServer.ping_topic % gateway_id
        ping_payload = PingPayload()
        ping_payload.gateway_id = gateway_id
        randstr = "ping" + str(random.randint(0, 10000)) + random.randint(0, 10000).to_bytes(4, 'big').hex()
        ping_payload.ping_id = base64.b64encode(randstr.encode()).decode()
        self.publish(ping_topic, ping_payload)
        self.gateways[gateway_id].num_pending_pings += 1
        gw_name = self.gateways[gateway_id].gateway.name
        self.app.print(f"PING EDGENODE {gw_name}")
        writeLog.info(f"PING EDGENODE {gw_name}")


    def check_nodes(self):
        current_timestamp = round(datetime.now().timestamp())
        if self.fault_detection:
            for gateway_id in self.gateways:
                interval_time = (current_timestamp - self.gateways[gateway_id].last_seen) * 1000
                if interval_time > AppServer.gateway_timout and self.gateways[gateway_id].active:
                    self.ping_gateway(gateway_id)
                if self.gateways[gateway_id].num_pending_pings >= 3 and self.gateways[gateway_id].active:
                    self.gateways[gateway_id].state = WorkingStateEnum.KO.name
                    self.gateways[gateway_id].active = False
                    gw_name = self.gateways[gateway_id].gateway.name
                    self.app.print(f"EDGENODE {gw_name} IS NOT WORKING. LAST POSITION: {self.gateways[gateway_id].GPS}")
                    writeLog.info(f"EDGENODE {gw_name} IS NOT WORKING. LAST POSITION: {self.gateways[gateway_id].GPS}")


    def close_connection(self):
        self.client.loop_stop()
        self.client.disconnect()

    # call back functions
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.connected_flag = True
            self.app.print(f"Connected OK Returned code={rc}")
            writeLog.info(f"Connected OK Returned code={rc}")
        else:
            self.app.print(f"Bad connection Returned code={rc}")

    def on_connect_fail(self):
        self.app.print(f"AppServer connection failed")

    def on_disconnect(self, client, userdata, rc):
        self.app.print(f"AppServer disconnected with code={rc}")

    def on_message(self, client, userdata, msg):
        self.app.print(f"AppServer received message from topic: {msg.topic}")
        writeLog.info(f"AppServer received message from topic: {msg.topic}")
        topic_splitted = msg.topic.split("/")
        topic_type = topic_splitted[-2] + topic_splitted[-1]
        payload_decoded = json.loads(msg.payload.decode())
        
        if topic_type == "eventjoin":
            dev_eui_decoded = payload_decoded['deviceInfo']['devEui'] 
            self.watchdogs[dev_eui_decoded] = get_watchdog_app_server(payload_decoded)
        
        elif topic_type == "eventup": 
            newBattery = self.monitoring(payload_decoded)
            newConfiguration, newBatteryConfig = self.analize_planning(newBattery)
            self.execute(payload_decoded, newConfiguration, newBatteryConfig)
        
        elif topic_type == "eventecho":
            self.gateways[payload_decoded['gateway_id']].last_seen = round(datetime.now().timestamp())
            self.gateways[payload_decoded['gateway_id']].num_pending_pings = 0
            self.gateways[payload_decoded['gateway_id']].state = WorkingStateEnum.OK.name
            self.gateways[payload_decoded['gateway_id']].active = True
            
        elif topic_type == "silentwatchdog":
            watchdog_name = self.watchdogs[payload_decoded['dev_eui_watchdog']].watchdog.deviceName
            watchdog_gps =  self.watchdogs[payload_decoded['dev_eui_watchdog']].GPS
            self.app.print(f"WATCHDOG {watchdog_name} IS SILENT. LAST POSITION: {watchdog_gps}")
            writeLog.info(f"WATCHDOG {watchdog_name} IS SILENT. LAST POSITION: {watchdog_gps}")

        elif topic_type == "eventstatus": # no longer used because we put 0 in the chirpstack interface in device-profile
            dev_eui_decoded = payload_decoded['deviceInfo']['devEui'] 
            self.watchdogs[dev_eui_decoded].watchdog.batteryLevel = payload_decoded['batteryLevel']
            self.watchdogs[dev_eui_decoded].watchdog.batteryLevelUnavailable = False if payload_decoded['batteryLevel'] is not None else True
            self.watchdogs[dev_eui_decoded].watchdog.margin = payload_decoded['margin']
            self.watchdogs[dev_eui_decoded].last_seen = round(datetime.now().timestamp())
            self.send_configuration(dev_eui_decoded)


    def monitoring(self, payload_decoded):
        dev_eui = payload_decoded['deviceInfo']['devEui']
        self.watchdogs[dev_eui].last_seen = round(datetime.now().timestamp())
        self.watchdogs[dev_eui].active = True
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.watchdogs[dev_eui].sensorData[date] = {"gps" : {}}
        data = payload_decoded['data']
        message_decoded = base64.b64decode(data).decode()
        # if watchdog is physical -> p, message_decoded is the string sent by arduino (no json)
        # if watchdog is virtual -> v, message_decoded is the string sent by watchdog.py (yes json)
        watchdogType = payload_decoded['deviceInfo']['deviceName'][0] # first letter of the name
        if watchdogType == 'p': #received by physical watchdog
            splitMessage = message_decoded.split("|")
            for sensor in AppServer.sensors:
                if sensor == "latitude" or sensor == "longitude":
                    self.watchdogs[dev_eui].sensorData[date]["gps"][sensor] = splitMessage[AppServer.sensors.index(sensor)]
                else:
                    self.watchdogs[dev_eui].sensorData[date][sensor] = splitMessage[AppServer.sensors.index(sensor)]
            latid = splitMessage[7]
            longit = splitMessage[8]
            self.watchdogs[dev_eui].GPS["latitude"] = latid
            self.watchdogs[dev_eui].GPS["longitude"] = longit
            newBattery = float(splitMessage[9])
        else: #msg from virtual watchdog
            message_json = json.loads(message_decoded) 
            message_json["battery"] = message_json['battery'] / 254 * 100
            newBattery = message_json['battery']
            self.watchdogs[dev_eui].sensorData[date] = message_json
            self.watchdogs[dev_eui].GPS = message_json["GPS"]
        self.watchdogs[dev_eui].watchdog.batteryLevel = newBattery
        print("Watchdog " + dev_eui + " send: " +  str(message_decoded) + "\n")
        return newBattery


    def analize_planning(self, battery_level):
        '''
        The parameters Min-Time-to-Send and Min-Time-to-Receive are set to different values according to the watchdog battery level.
        There are 4 different conditions : 
        the battery is over 50%, they assume the lowest value which are MIN_TIME_TO_SEND and MIN_TIME_TO_RECEIVE
        the battery level is between 50% and 30%, the parameters are set to  MIN_TIME_TO_SEND * 1.5 and MIN_TIME_TO_RECEIVE * 1.5
        the battery level is between 30% and 15%, the parameters are set to  MIN_TIME_TO_SEND * 3 and MIN_TIME_TO_RECEIVE * 3
        the battery level is below 15%, the parameters are set to  MIN_TIME_TO_SEND * 5 and MIN_TIME_TO_RECEIVE * 5
        '''
        watchdog_configuration = DownlinkConfigurationPayload()
        if battery_level > 50:
            watchdog_configuration.timetosend = AppServer.MIN_TIME_TO_SEND
            watchdog_configuration.timetoreceive = AppServer.MIN_TIME_TO_RECEIVE
            batteryConfig = WatchdogBatteryConfigEnum.NORMAL.value

        elif battery_level > 30:
            watchdog_configuration.timetosend = round(AppServer.MIN_TIME_TO_SEND * 1.5)
            watchdog_configuration.timetoreceive = round(AppServer.MIN_TIME_TO_RECEIVE * 1.5)
            batteryConfig = WatchdogBatteryConfigEnum.SOFT_ENERGY_SAVING.value

        elif battery_level > 15:
            watchdog_configuration.timetosend = round(AppServer.MIN_TIME_TO_SEND * 3)
            watchdog_configuration.timetoreceive = round(AppServer.MIN_TIME_TO_RECEIVE * 3)
            batteryConfig = WatchdogBatteryConfigEnum.ENERGY_SAVING_.value

        else:
            watchdog_configuration.timetosend = round(AppServer.MIN_TIME_TO_SEND * 5)
            watchdog_configuration.timetoreceive = round(AppServer.MIN_TIME_TO_RECEIVE * 5)
            batteryConfig = WatchdogBatteryConfigEnum.HARD_ENERGY_SAVING.value

        return watchdog_configuration, batteryConfig



    def execute(self, payload_decoded, newConfiguration, newBatteryConfig):  
        '''
        0 - PM10;
        1 - TEMPERATURE;
        2 - HUMIDITY;
        3 - OZONE; impiega molto a fare la calibrazione quindi metto 0
        4 - BENZENE;
        5 - AMMONIA;
        6 - ALDEHYDES;
        7 - GPS;
        '''
        dev_eui = payload_decoded['deviceInfo']['devEui']
        if self.watchdogs[dev_eui].active and self.watchdogs[dev_eui].battery_config != newBatteryConfig: 
            self.watchdogs[dev_eui].battery_config = newBatteryConfig
            string_to_send = f"1|1|1|0|1|1|1|1|{newConfiguration.timetosend}|{newConfiguration.timetoreceive}"
            #string_to_send_encoded = base64.b64encode(string_to_send.encode()).decode() not needed in physics payload
            enqueue_device_downlink(dev_eui, 1, False, string_to_send) 
            device_name = self.watchdogs[dev_eui].watchdog.deviceName
            self.app.print(f"APPSERVER ENQUEQUE WATCHDOG {device_name} CONFIGURATION")
            writeLog.info(f"APPSERVER ENQUEQUE WATCHDOG {device_name} CONFIGURATION")


    def to_json(self): 
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
