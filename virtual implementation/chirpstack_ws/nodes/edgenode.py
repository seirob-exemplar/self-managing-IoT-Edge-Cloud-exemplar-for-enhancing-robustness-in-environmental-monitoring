import base64
import json
import random
import time
from datetime import datetime
from types import SimpleNamespace
from typing import TypeVar

from paho.mqtt.client import Client

from enums.working_state_enum import WorkingStateEnum
from enums.connection_state_enum import ConnectionStateEnum
from enums.crc_status_enum import CRCStatusEnum
from enums.tx_ack_status_enum import TxAckStatusEnum
# Payload message types
from payloads.edgenode.conn_payload import ConnPayload
from payloads.edgenode.echo_payload import EchoPayload
from payloads.info.rx_info import RxInfo
from payloads.info.tx_info import TxInfo
from payloads.edgenode.stats_payload import StatsPayload
from payloads.edgenode.tx_ack_item_payload import TxAckItemPayload
from payloads.edgenode.tx_ack_payload import TxAckPayload
from payloads.edgenode.up_payload import UpPayload
from payloads.edgenode.silent_payload import SilentPayload
from utils.payload_util import get_json_from_object

from appserver.watchdog_appserver import WatchdogAppServer
from nodes.watchdog import Watchdog

import logger
writeLog = logger.getLogger("edgenode.log")

T = TypeVar('T')

class EdgeNode:
    # Number of gateways
    number_of_gw = 0

    # Topics
    conn_topic =    "eu868/gateway/%s/state/conn"
    up_topic =      "eu868/gateway/%s/event/up"
    ack_topic =     "eu868/gateway/%s/event/ack"
    stats_topic =   "eu868/gateway/%s/event/stats"
    echo_topic =    "eu868/gateway/%s/event/echo"
    down_topic =    "eu868/gateway/%s/command/down"
    ping_topic =    "eu868/gateway/%s/command/ping"
    silentWD_topic= "eu868/gateway/%s/silent/watchdog"
    
    #join_topic = "application/%s/device/%s/event/join" 
    up_app_topic = "application/%s/device/%s/event/up"

    watchdog_timeout = 60000

    def __init__(self, broker="", port=None, id_gateway="", name="", ip="", organization_id=None,
                 network_server_id=None, gateway_app=None, GPS={"latitude":None, "longitude":None} ):
        self.broker = broker
        self.port = port
        self.ip = ip
        self.client = None
        self.client_id = "loragateway_" + str(datetime.now().timestamp()) + "_" + str(EdgeNode.number_of_gw)
        self.username = "chirpstack_gw"
        self.password = ""
        # other fields
        self.id_gateway = id_gateway
        self.name = name
        self.encoded_id_gateway = base64.b64encode(int(id_gateway, 16).to_bytes(8, 'big')).decode()
        self.organization_id = organization_id
        self.network_server_id = network_server_id
        self.can_sand_data = False
        self.rxPacketsReceived = 0  # Number of radio packets received.
        self.rxPacketsReceivedOK = 0  # Number of radio packets received with valid PHY CRC.
        self.txPacketsReceived = 0  # Number of downlink packets received for transmission.
        self.txPacketsEmitted = 0  # Number of downlink packets emitted.
        self.GPS = GPS
        self.watchdogs:dict[WatchdogAppServer] = {} # Watchdog type
        self.app = gateway_app
        EdgeNode.number_of_gw += 1

    def start_connection(self):
        try:
            # Set Connecting Client ID
            self.client = Client(client_id=self.client_id, clean_session=True)
            self.client.username_pw_set(self.username, self.password)
            # call back functions
            self.client.on_connect = self.on_connect
            self.client.on_connect_fail = self.on_connect_fail
            self.client.on_publish = self.on_publish
            self.client.on_disconnect = self.on_disconnect
            self.client.on_subscribe = self.on_subscribe
            self.client.on_message = self.on_message

            self.app.print(f"Edgenode {self.name} connecting : {self.client.connect(self.broker, self.port, 60)}")
            writeLog.info(f"Edgenode {self.name} connecting : {self.client.connect(self.broker, self.port, 60)}")

            time.sleep(1)
            self.client.loop_start()
            while not self.client.is_connected(): 
                time.sleep(1)

            self.app.print(f"Edgenode {self.name} connected!")
            writeLog.info(f"Edgenode {self.name} connected!")
        except BaseException as err:
            self.app.print(f"ERROR: Edgenode {self.id_gateway} Could not connect to MQTT.")
            self.app.print(f"Unexpected {err=}, {type(err)=}")
            self.close_connection()

    def conn_publish(self, state=ConnectionStateEnum.OFFLINE.name):
        conn_topic = EdgeNode.conn_topic % self.id_gateway

        # payload setting
        conn_payload = ConnPayload()
        conn_payload.state = state
        conn_payload.gatewayId = self.id_gateway

        return self.publish(conn_topic, conn_payload)

    def stats_publish(self):
        stats_topic = EdgeNode.stats_topic % self.id_gateway
        # payload setting
        stats_payload = StatsPayload()
        stats_payload.gatewayId = self.id_gateway
        stats_payload.time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        return self.publish(stats_topic, stats_payload)

    def up_link_publish(self, phy_payload, tx_info=TxInfo()):
        up_topic = EdgeNode.up_topic % self.id_gateway
        # payload setting
        #randstr = str(random.randint(0, 10000)) + random.randint(0, 10000).to_bytes(4, 'big').hex()
        uplink_id = random.randint(1,9999) #base64.b64encode(randstr.encode()).decode()
        rx_info = RxInfo(gateway_id=self.id_gateway, time=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                     uplink_id=uplink_id)
        up_link_payload = UpPayload(phy_payload=phy_payload, tx_info=tx_info, rx_info=rx_info)

        return self.publish(up_topic, up_link_payload)

    def tack_message_publish(self, tx_ack_status, downlink_id):#,token)
        ack_topic = EdgeNode.ack_topic % self.id_gateway
        tx_ack_payload = TxAckPayload()
        tx_ack_payload.gatewayId = self.id_gateway
        tx_ack_payload.items.append(TxAckItemPayload(tx_ack_status.name))
        #tx_ack_payload.token = token
        tx_ack_payload.downlinkId = downlink_id
        return self.publish(ack_topic, tx_ack_payload)

    def echo_message_publish(self, gateway_id, ping_id):
        echo_topic = EdgeNode.echo_topic % self.id_gateway
        echo_payload = EchoPayload()
        echo_payload.gateway_id = gateway_id
        echo_payload.ping_id = ping_id
        return self.publish(echo_topic, echo_payload)

    def publish(self, topic, payload: T):
        if self.client is None:
            return False
        if not self.client.is_connected():
            self.app.print(f"Edgenode {self.id_gateway} not connected")
            return False
        # json conversion
        json_payload = get_json_from_object(payload)
        message = json.dumps(json_payload)

        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            self.app.print(f"Edgenode {self.name} send message to topic {topic}")
            writeLog.info(f"Edgenode {self.name} send message to topic {topic}")
            return True

        self.app.print(f"Edgenode {self.id_gateway} failed to send message to topic {topic}")
        return False

    def subscribe(self):
        down_topic_to_sub = EdgeNode.down_topic % self.id_gateway
        ping_topic_to_sub = EdgeNode.ping_topic % self.id_gateway
        up_topic_to_sub = EdgeNode.up_topic % self.id_gateway
        self.client.subscribe(down_topic_to_sub)
        self.client.subscribe(ping_topic_to_sub)
        #self.client.subscribe(up_topic_to_sub)

    def subscribe_to_appServer_topic(self, id_app, dev_eui):
        up_topic_to_sub = EdgeNode.up_app_topic % (id_app, dev_eui)
        #join_topic_to_sub = EdgeNode.join_topic % (id_app, dev_eui)
        self.client.subscribe(up_topic_to_sub)
        #self.client.subscribe(join_topic_to_sub)

    def close_connection(self):
        if self.client is not None:
            self.conn_publish(ConnectionStateEnum.OFFLINE.name)
            self.client.loop_stop()
            self.client.disconnect()

    def check_nodes(self):
        """verify that nodes are active or not"""
        current_timestamp = round(datetime.now().timestamp())
        for dev_eui in self.watchdogs:
            if self.watchdogs[dev_eui].active == True: 
                self.analize_planning(current_timestamp, dev_eui)
                self.execute(dev_eui)
                

    def analize_planning(self, current_timestamp, dev_eui):
        interval_time = (current_timestamp - self.watchdogs[dev_eui].last_seen) * 1000
        if interval_time > EdgeNode.watchdog_timeout:
            self.watchdogs[dev_eui].num_failure += 1        


    def execute(self, dev_eui):  
        if self.watchdogs[dev_eui].num_failure >= 3:
            self.watchdogs[dev_eui].state = WorkingStateEnum.KO.name
            self.watchdogs[dev_eui].active = False
            wd_name = self.watchdogs[dev_eui].watchdog.deviceName
            self.app.print(f"Edgenode {self.name}: WATCHDOG {wd_name} IS SILENT. LAST POSITION: {self.watchdogs[dev_eui].GPS}")
            writeLog.info(f"Edgenode {self.name}: WATCHDOG {wd_name} IS SILENT. LAST POSITION: {self.watchdogs[dev_eui].GPS}")
            #notify the appserver
            silent_topic = EdgeNode.silentWD_topic % self.id_gateway
            silent_payload = SilentPayload()
            silent_payload.dev_eui_watchdog = dev_eui
            silent_payload.idGateway = self.id_gateway
            self.publish(silent_topic, silent_payload)


    # call back functions
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.connected_flag = True
            self.app.print(f"Connected OK Returned code={rc}")
            writeLog.info(f"Connected OK Returned code={rc}")
        else:
            self.app.print(F"Bad connection Returned code={rc}")

    def on_connect_fail(self):
        self.app.print(f"Edgenode {self.id_gateway} failed connection")

    def on_publish(self, client, userdata, mid):
        self.txPacketsReceived += 1

    def on_disconnect(self, client, userdata, rc):
        self.app.print(f"Edgenode {self.id_gateway} disconnected with code={rc}")
        writeLog.info(f"Edgenode {self.id_gateway} disconnected with code={rc}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.app.print(f"Edgenode {self.name} Subscribed to topic {mid}")
        writeLog.info(f"Edgenode {self.name} Subscribed to topic {mid}")

    def on_message(self, client, userdata, msg):
        self.app.print(f"Edgenode {self.name} received message from topic: {msg.topic}")
        writeLog.info(f"Edgenode {self.name} received message from topic: {msg.topic}")
        down_topic_to_sub = EdgeNode.down_topic % self.id_gateway
        ping_topic_to_sub = EdgeNode.ping_topic % self.id_gateway
        up_topic_to_sub = EdgeNode.up_topic % self.id_gateway
        
        try:
            message_decoded = json.loads(msg.payload.decode()) 
            if msg.topic == down_topic_to_sub:
                phy_payload = message_decoded['items'][0]['phyPayload'] 
                result = False
                for watchdog_AP in self.watchdogs.values():
                    if watchdog_AP.watchdog.deviceName[0] == 'v': 
                        tx_info_str = json.dumps(message_decoded['items'][0]['txInfo']) 
                        tx_info = json.loads(tx_info_str, object_hook=lambda d: SimpleNamespace(**d))
                        result = result or watchdog_AP.watchdog.receive_message(phy_payload, tx_info)
                if result:
                    self.tack_message_publish(TxAckStatusEnum.OK, message_decoded['downlinkId'])#, message_decoded['token'])
                if msg.state == 0:
                    self.rxPacketsReceivedOK += 1
                self.rxPacketsReceived += 1
            elif msg.topic == ping_topic_to_sub:
                self.echo_message_publish(message_decoded['gateway_id'], message_decoded['ping_id'])
            else: # topic like application/+/device/+/event/+ 
                topic_splitted = msg.topic.split("/")
                self.monitoring(message_decoded, topic_splitted)

        except Exception as e:
            print("Payload from a physical watchdog")

    def monitoring(self, message_decoded, topic_splitted):
        gateway_used = message_decoded['rxInfo'][0]['gatewayId']
        if gateway_used == self.id_gateway: # the message arrived to the server via this gateway
            topic_type = topic_splitted[0] + "_" + topic_splitted[-2] + topic_splitted[-1]
            if topic_type == "application_eventup": # add the watchdog to the dict of watchdogs and update it
                dev_eui = message_decoded['deviceInfo']['devEui'] 
                if dev_eui not in self.watchdogs: # add the watchdog to the dict
                    watchdog = Watchdog(application_id=message_decoded['deviceInfo']['applicationId'],
                                        device_name=message_decoded['deviceInfo']['deviceName'],
                                        dev_eui=message_decoded['deviceInfo']['devEui'], 
                                        dev_addr=message_decoded['devAddr']) 
                    watchdog_appServer = WatchdogAppServer()
                    watchdog_appServer.watchdog = watchdog
                    self.watchdogs[dev_eui] = watchdog_appServer
                # update the watchdog
                self.watchdogs[dev_eui].last_seen = round(datetime.now().timestamp())
                self.watchdogs[dev_eui].active = True
                watchdogType = message_decoded['deviceInfo']['deviceName'][0]
                data = message_decoded['data']
                data_decoded = base64.b64decode(data).decode()
                if watchdogType == 'p':
                    splitMessage = data_decoded.split("|")
                    latid = splitMessage[7]
                    longit = splitMessage[8]
                    self.watchdogs[dev_eui].GPS["latitude"] = latid
                    self.watchdogs[dev_eui].GPS["longitude"] = longit
                else:
                    message_json = json.loads(data_decoded) 
                    self.watchdogs[dev_eui].GPS = message_json["GPS"]     

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
