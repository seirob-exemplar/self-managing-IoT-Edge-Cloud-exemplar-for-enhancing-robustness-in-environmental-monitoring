import time
from threading import Thread

from enums.bcolors import BColors
from utils.api_utils import get_device_key
from nodes.watchdog import Watchdog


def get_decrease_battery_level(timetosend, spreading_factor, power):
    return 1 + round(20000/timetosend)


class ThreadWatchdog(Thread):
    def __init__(self, watchdog:Watchdog, thread_lock, critical_section_lock):
        Thread.__init__(self)
        self.watchdog = watchdog
        self.threadLock = thread_lock  # serve per non accedere allo stesso gateway contemporaneamente
        self.criticalSectionLock = critical_section_lock
        self._running = True
        self.previousMillisS = 0
        self.previousMillisR = 0
        self.previousMillisBatteryUpdate = 0
        self.timetoupdate = 2000
        self.start_time = time.time()
        self.finish_time = time.time()
        self.app = None

    def run(self):
        result = False
        resp = get_device_key(self.watchdog.devEUI)
        self.watchdog.app_key = resp.device_keys.nwk_key
        self.watchdog.app = self.app
        fail_count = 0
        while not result:
            self.threadLock.acquire()
            result = self.watchdog.join()
            self.threadLock.release()
            fail_count += 1
            if fail_count >= 3:
                self.stop()
                break
            time.sleep(5)
        while self._running:
            current_millis = round(time.time() * 1000)

            if self.watchdog.batteryLevel <= 0:
                self.stop()
                break

            if (current_millis - self.previousMillisBatteryUpdate) > self.timetoupdate:
                spreading_factor = None
                power = None
                self.previousMillisBatteryUpdate = current_millis
                if self.watchdog.txInfo is not None:
                    spreading_factor = self.watchdog.txInfo.modulation.lora.spreadingFactor
                    #power = self.watchdog.txInfo.power

                self.watchdog.batteryLevel -= get_decrease_battery_level(self.watchdog.timetosend, spreading_factor, power)
                self.watchdog.batteryLevel = max(self.watchdog.batteryLevel, 0)

            if (current_millis - self.previousMillisS) > self.watchdog.timetosend:
                self.criticalSectionLock.acquire()
                self.threadLock.acquire()
                self.watchdog.send_data()
                self.threadLock.release()
                self.criticalSectionLock.release()
                self.previousMillisS = current_millis
            time.sleep(2)

    def stop(self):
        if self._running:
            self.finish_time = time.time()
            self._running = False
            life_time = round((self.finish_time - self.start_time)/60, 2)
            print(f"{BColors.HEADER.value}{BColors.UNDERLINE.value}THREAD WATCHDOG {self.watchdog.deviceName} "
                  f"STOPPED - LIFE TIME {life_time} minutes {BColors.ENDC.value}")
            self.app.print(f"THREAD WATCHDOG {self.watchdog.deviceName} STOPPED - LIFE TIME {life_time} minutes")
