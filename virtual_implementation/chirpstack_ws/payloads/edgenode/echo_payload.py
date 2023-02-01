import json


class EchoPayload:
    def __init__(self, gateway_id="", ping_id=None):
        self.gateway_id = gateway_id
        self.ping_id = ping_id

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)