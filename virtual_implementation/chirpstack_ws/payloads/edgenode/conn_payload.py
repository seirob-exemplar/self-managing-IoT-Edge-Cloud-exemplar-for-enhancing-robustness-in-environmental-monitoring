import json


class ConnPayload:
    def __init__(self, gateway_id="", state=""):
        self.gatewayId = gateway_id  # encoded base64 standard
        self.state = state

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
