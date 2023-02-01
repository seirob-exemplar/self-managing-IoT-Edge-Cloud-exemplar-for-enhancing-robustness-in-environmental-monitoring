import json
from enums.working_state_enum import WorkingStateEnum


class GatewayAppServer:
    def __init__(self, gateway=None, last_seen=None, state=WorkingStateEnum.OK.value, active=False, num_pending_pings=0):
        self.gateway = gateway
        self.last_seen = last_seen
        self.state = state
        self.active = active
        self.num_pending_pings = num_pending_pings
        self.GPS = {"latitude":None, "longitude":None}

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
