import json


class DownCommandPayload:
    def __init__(self, confirmed=False, f_port=1, data=""):
        self.confirmed = confirmed
        self.fPort = f_port
        self.data = data

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
