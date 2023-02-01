import time
from threading import Thread

from enums.bcolors import BColors
from nodes.edgenode import EdgeNode


class ThreadEdgenode(Thread):
    def __init__(self, gateway:EdgeNode, gateway_app=None):
        Thread.__init__(self)
        self.gateway = gateway
        self._running = True
        self.app = gateway_app

    def init_subscribe(self, id_application, devices=[]):
        for device in devices:
            self.gateway.subscribe_to_appServer_topic(id_application , device.dev_eui)
        self.gateway.subscribe()

    def run(self):
        count = 0
        while self._running:
            if count % 5 == 0: 
                self.gateway.stats_publish()
                if len(self.gateway.watchdogs) > 0:
                    self.gateway.check_nodes()
                count = 0
            count += 1
            time.sleep(10)

    def stop(self):
        if self._running:
            self._running = False
            self.gateway.close_connection()
            print(f"{BColors.OKCYAN.value}{BColors.UNDERLINE.value}THREAD EDGENODE {self.gateway.id_gateway} STOPPED{BColors.ENDC.value}")
