import json
from enums.watchdog_battery_config_enum import WatchdogBatteryConfigEnum
from enums.working_state_enum import WorkingStateEnum



class WatchdogAppServer:
    def __init__(self, watchdog=None, last_seen=None, state=WorkingStateEnum.OK.value,
                 battery_config=WatchdogBatteryConfigEnum.NORMAL.value, active=False, num_failure=0):
        self.watchdog = watchdog
        self.last_seen = last_seen
        self.state = state
        self.battery_config = battery_config
        self.active = active
        self.num_failure = num_failure
        self.GPS = {"latitude":None, "longitude":None}
        self.sensorData:dict = {} # dict of data received by this watchdog key -> date, value -> sensors value

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
