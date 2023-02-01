import json


class SilentPayload:
    def __init__(self, dev_eui_watchdog="", idGateway="" ):
        self.dev_eui_watchdog = dev_eui_watchdog
        self.idGateway = idGateway
        

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)