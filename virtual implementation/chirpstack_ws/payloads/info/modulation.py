import json
from payloads.info.lora import Lora 


class Modulation:
    def __init__(self):
        self.lora = Lora()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
