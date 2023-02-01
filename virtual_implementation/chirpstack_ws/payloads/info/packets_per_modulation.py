import json

from payloads.info.modulation import Modulation


class PacketsPerModulation:
    def __init__(self, modulation=Modulation(), count=1):
        self.modulation = modulation
        self.count = count

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
