import json


class TxAckPayload:
    def __init__(self, gateway_id="", token="", downlink_id=""):
        self.gatewayId = gateway_id
        #self.token = token
        self.items = []
        self.downlinkId = downlink_id

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
