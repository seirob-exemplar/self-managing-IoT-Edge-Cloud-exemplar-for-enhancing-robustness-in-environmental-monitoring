import json


class PacketsPerStatus:
    def __init__(self, ok=1):
        self.OK = ok

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
