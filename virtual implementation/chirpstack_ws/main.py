"""Main module starting the application"""
import math
import threading
import time
import setup
from tkinter import *
from datetime import datetime
from enums.connection_state_enum import ConnectionStateEnum
from gui.console_log_application import ConsoleLogApplication
from nodes.watchdog import Watchdog
from appserver.appserver import AppServer
from appserver.watchdog_appserver import WatchdogAppServer
from nodes.edgenode import EdgeNode
from threads.thread_appserver import ThreadAppServer
from threads.thread_watchdog import ThreadWatchdog
from threads.thread_edgenode import ThreadEdgenode
from utils.api_utils import get_device_key, get_device_list, get_gateway_list


GPS = [{"lat":45.6472792, "longi":9.5944264}, {"lat":45.646946, "longi":9.598237}]


def get_devices():
    limit = 100
    offset = 0
    device_list = []
    while True:
        resp = get_device_list(setup.application_id, limit, offset)
        device_list.extend(resp.result)
        if resp.total_count <= (len(resp.result) + offset):
            break
        offset += len(resp.result)
    return device_list


def get_gateways():
    limit = 100
    offset = 0
    gateway_list = []
    while True:
        resp = get_gateway_list(limit, offset)
        gateway_list.extend(resp.result)
        if resp.total_count <= (len(resp.result) + offset):
            break
        offset += len(resp.result)
    return gateway_list


def activate_watchdogs(watchdog_list):
    for watchdog in watchdog_list:
        resp = get_device_key(watchdog.devEUI)
        watchdog.app_key = resp.device_keys.nwk_key
        watchdog.join()


def assign_virtualWatchdogs_to_gateways(watchdog_list:list[Watchdog], gateway_list:list[EdgeNode]):
    devices_per_gateway = math.ceil( len(watchdog_list)/len(gateway_list) )
    thread_watchdog_list = []
    thread_gateway_list = []

    i = 0
    j = -1

    while i < len(watchdog_list):
        if i % devices_per_gateway == 0 and i >= 0: # add new Thread_Edgenode
            thread_lock = threading.Lock()
            j += 1
            thread_edgenode = ThreadEdgenode(gateway_list[j])
            thread_gateway_list.append(thread_edgenode)
        
        critical_section_lock = threading.Lock()
        watchdogType = watchdog_list[i].deviceName[0]
        if watchdogType == 'v':
            thread_watchdog = ThreadWatchdog(watchdog_list[i], thread_lock, critical_section_lock) 
            thread_watchdog.watchdog.sensorsActiveFlags["GPS"]["latitude"] = GPS[i]["lat"]
            thread_watchdog.watchdog.sensorsActiveFlags["GPS"]["longitude"] = GPS[i]["longi"]
            thread_watchdog_list.append(thread_watchdog)

        watchdog_list[i].gateways.append(gateway_list[j])
        watchdog_appServer = WatchdogAppServer()
        watchdog_appServer.watchdog = watchdog_list[i]
        #watchdog_appServer.last_seen = round(datetime.now().timestamp())
        watchdog_appServer.active = False # become true when I press the start watchdogs button
        gateway_list[j].watchdogs[watchdog_list[i].devEUI] =watchdog_appServer

        i += 1

    return thread_watchdog_list, thread_gateway_list


def assign_watchdogs_to_gateways_full_connected(watchdog_list, gateway_list):
    thread_watchdog_list = []
    thread_gateway_list = []

    first = True
    for gateway in gateway_list:
        thread_lock = threading.Lock()
        thread_edgenode = ThreadEdgenode(gateway)
        for watchdog in watchdog_list:
            if first:
                critical_section_lock = threading.Lock()
                thread_watchdog = ThreadWatchdog(watchdog, thread_lock, critical_section_lock)
                thread_watchdog_list.append(thread_watchdog)

            watchdog.gateways.append(gateway)
            gateway.watchdogs.append(watchdog)

        first = False
        thread_gateway_list.append(thread_edgenode)
    return thread_watchdog_list, thread_gateway_list


def terminate_gateway_threads(thread_gateway_list):
    for thread_gateway in thread_gateway_list:
        thread_gateway.stop()
        thread_gateway.gateway.client = None


def terminate_watchdog_threads(thread_watchdog_list):
    for thread_watchdog in thread_watchdog_list:
        thread_watchdog.criticalSectionLock.acquire()
        thread_watchdog.stop()
        thread_watchdog.criticalSectionLock.release()


def main():
    # get nodes
    devices = get_devices()
    gateways = get_gateways()

    # print("gateway -> " +  str(gateways))
    # print("watchdog ->" + str(devices))

    # App Server
    app_root = Tk()
    app_root.geometry("600x600")
    app_root.resizable(True, True)
    app_root.title("Environmental monitoring")
    # app_server_app = ConsoleLogApplication(app_root, "#56D548", "green", "APP SERVER CONSOLE LOG")
    app_server = AppServer(broker=setup.broker_server, port=setup.port, id_application=setup.application_id, ip=setup.ip)

    # Node list creation
    # Gateway
    # gateway_app = ConsoleLogApplication(app_root, "#128fe3", "#12c4e3", "GATEWAY CONSOLE LOG")
    gateway_list:list[EdgeNode] = []
    for gw in gateways:
        gateway = EdgeNode(broker=setup.broker_gw, port=setup.port, id_gateway=gw.gateway_id, name=gw.name,
                           organization_id=gw.tenant_id,
                           network_server_id=gw.tenant_id,
                           GPS={"latitude":gw.location.latitude, "longitude":gw.location.longitude})
        gateway_list.append(gateway)

    # Watchdog
    # watchdog_app = ConsoleLogApplication(app_root, "#e01bd0", "#fc03f0", "WATCHDOG CONSOLE LOG")
    virtual_watchdog_list:list[Watchdog] = []
    for device in devices:
        if device.name[0] == 'v':
            virtual_watchdog_list.append(Watchdog(application_id=setup.application_id, device_name=device.name,
                                            device_profile_id=device.device_profile_id, dev_eui=device.dev_eui,
                                            battery_level_unavailable=False, battery_level=244,
                                            margin=device.device_status.margin))
    
    thread_watchdog_list:list[ThreadWatchdog]
    thread_gateway_list:list[ThreadEdgenode]
    thread_watchdog_list, thread_gateway_list = assign_virtualWatchdogs_to_gateways(virtual_watchdog_list, gateway_list) 
    thread_app_server:ThreadAppServer = ThreadAppServer(app_server)

    # starting thread functions
    def start_threads_gateway(start_button_gateway_to_destroy, stop_call_back, button):
        gateway_window = Toplevel(app_root)
        gateway_window.geometry("1000x300")
        gateway_window.title("Environmental monitoring: Gateways")

        def on_closing():
            stop_call_back(button)
            gateway_window.destroy()

        gateway_window.protocol("WM_DELETE_WINDOW", on_closing)
        gateway_app = ConsoleLogApplication(gateway_window, "#128fe3", "#12c4e3", "GATEWAY CONSOLE LOG")
        for thread_gateway in thread_gateway_list:
            thread_gateway.app = gateway_app
            thread_gateway.gateway.app = gateway_app
            thread_gateway.gateway.start_connection()
            thread_gateway.init_subscribe(id_application=setup.application_id,devices=devices)
            thread_gateway.gateway.conn_publish(ConnectionStateEnum.ONLINE.name)
            thread_gateway.start()
        start_button_gateway_to_destroy.destroy()

    def stop_threads_gateway(stop_button_gateway_to_destroy):
        terminate_gateway_threads(thread_gateway_list)
        stop_button_gateway_to_destroy.destroy()

    stop_button_gateway = Button(app_root, text="Stop gateways",
                                 command=lambda: stop_threads_gateway(stop_button_gateway))
    stop_button_gateway.pack({"side": "bottom", "expand": "no"})
    start_button_gateway = Button(app_root, text="Start gateways",
                                  command=lambda: start_threads_gateway(start_button_gateway,
                                                                        stop_threads_gateway,
                                                                        stop_button_gateway))
    start_button_gateway.pack({"side": "bottom", "expand": "no"})



    def start_threads_watchdog(start_button_watchdog_to_destroy, stop_call_back, button):
        watchdog_window = Toplevel(app_root)
        watchdog_window.title("Environmental monitoring: Watchdogs")
        watchdog_window.geometry("700x300")

        def on_closing():
            stop_call_back(button)
            watchdog_window.destroy()

        watchdog_window.protocol("WM_DELETE_WINDOW", on_closing)
        watchdog_app = ConsoleLogApplication(watchdog_window, "#e01bd0", "#fc03f0", "WATCHDOG CONSOLE LOG")
        for thread_gateway in thread_gateway_list:
            for watchdog_AP in thread_gateway.gateway.watchdogs.values():
                watchdog_AP.last_seen = round(datetime.now().timestamp())
                watchdog_AP.active = True
        for thread_watchdog in thread_watchdog_list:
            thread_watchdog.watchdog.app = watchdog_app
            thread_watchdog.app = watchdog_app
            thread_watchdog.start()
            time.sleep(2)
        
        start_button_watchdog_to_destroy.destroy()

    def stop_threads_watchdog(stop_button_watchdog_to_destroy):
        terminate_watchdog_threads(thread_watchdog_list)
        stop_button_watchdog_to_destroy.destroy()

    stop_button_watchdog = Button(app_root, text="Stop watchdogs",
                                  command=lambda: stop_threads_watchdog(stop_button_watchdog))
    stop_button_watchdog.pack({"side": "left", "expand": "no"})
    start_button_watchdog = Button(app_root, text="Start watchdogs",
                                   command=lambda: start_threads_watchdog(start_button_watchdog,
                                                                          stop_threads_watchdog,
                                                                          stop_button_watchdog))
    start_button_watchdog.pack({"side": "left", "expand": "no"})



    def start_thread_app_server(start_button_to_destroy, stop_call_back, button):
        app_server_window = Toplevel(app_root)
        app_server_window.title("Environmental monitoring: App Server")
        app_server_window.geometry("900x300")

        def on_closing():
            stop_call_back(button)
            app_server_window.destroy()

        app_server_window.protocol("WM_DELETE_WINDOW", on_closing)
        app_server_app = ConsoleLogApplication(app_server_window, "#56D548", "green", "APP SERVER CONSOLE LOG")
        thread_app_server.app_server.app = app_server_app
        thread_app_server.app = app_server_app
        thread_app_server.init_app_server(devices, gateway_list)
        thread_app_server.start()
        start_button_to_destroy.destroy()

    def stop_thread_app_server(stop_button_to_destroy):
        thread_app_server.stop()
        stop_button_to_destroy.destroy()

    if setup.app_server_enabled:
        stop_button = Button(app_root, text="Stop App Server",
                             command=lambda: stop_thread_app_server(stop_button))
        stop_button.pack({"side": "right", "expand": "no"})
        start_button = Button(app_root, text="Start App Server",
                              command=lambda: start_thread_app_server(start_button, stop_thread_app_server,
                                                                      stop_button))
        start_button.pack({"side": "right", "expand": "no"})

    app_root.mainloop()


if __name__ == "__main__":
    main()
