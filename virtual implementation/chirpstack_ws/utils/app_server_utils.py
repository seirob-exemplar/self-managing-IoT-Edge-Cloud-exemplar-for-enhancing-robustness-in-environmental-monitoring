from datetime import datetime
import base64

from enums.watchdog_battery_config_enum import WatchdogBatteryConfigEnum
from nodes.watchdog import Watchdog
from appserver.watchdog_appserver import WatchdogAppServer
from payloads.mac_layer.downlink_configuration_payload import DownlinkConfigurationPayload

MIN_TIME_TO_SEND = 10000 # MAX 200.000
MIN_TIME_TO_RECEIVE = 10000 # MAX 200.000


def get_watchdog_app_server(payload_msg):
    watchdog_app_server = WatchdogAppServer()
    watchdog = Watchdog(application_id=payload_msg['deviceInfo']['applicationId'],
                        device_name=payload_msg['deviceInfo']['deviceName'],
                        dev_eui=payload_msg['deviceInfo']['devEui'], 
                        dev_addr=payload_msg['devAddr'])
    watchdog_app_server.watchdog = watchdog
    watchdog_app_server.last_seen = round(datetime.now().timestamp())
    return watchdog_app_server

                        

def get_watchdog_configuration(battery_level):
    watchdog_configuration = DownlinkConfigurationPayload()
    
    #battery_level = watchdog_app_server.watchdog.batteryLevel
    if battery_level > 50:
        watchdog_configuration.timetosend = MIN_TIME_TO_SEND
        watchdog_configuration.timetoreceive = MIN_TIME_TO_RECEIVE
        batteryConfig = WatchdogBatteryConfigEnum.NORMAL.value
        #watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.NORMAL.value
    elif battery_level > 30:
        watchdog_configuration.timetosend = round(MIN_TIME_TO_SEND * 1.5)
        watchdog_configuration.timetoreceive = round(MIN_TIME_TO_RECEIVE * 1.5)
        batteryConfig = WatchdogBatteryConfigEnum.SOFT_ENERGY_SAVING.value
        #watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.SOFT_ENERGY_SAVING.value
    elif battery_level > 15:
        watchdog_configuration.timetosend = round(MIN_TIME_TO_SEND * 3)
        watchdog_configuration.timetoreceive = round(MIN_TIME_TO_RECEIVE * 3)
        batteryConfig = WatchdogBatteryConfigEnum.ENERGY_SAVING_.value
        #watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.ENERGY_SAVING_.value
    else:
        watchdog_configuration.timetosend = round(MIN_TIME_TO_SEND * 5)
        watchdog_configuration.timetoreceive = round(MIN_TIME_TO_RECEIVE * 5)
        batteryConfig = WatchdogBatteryConfigEnum.HARD_ENERGY_SAVING.value
        #watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.HARD_ENERGY_SAVING.value

    return watchdog_configuration, batteryConfig
