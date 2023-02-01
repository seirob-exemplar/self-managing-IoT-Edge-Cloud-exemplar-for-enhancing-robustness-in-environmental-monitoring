import json


class TxAckItemPayload:
    def __init__(self, status=""):
        self.status = status

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
