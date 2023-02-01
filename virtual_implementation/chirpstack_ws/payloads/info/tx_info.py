import json

from payloads.info.modulation import Modulation


class DelayTimingInfo:
    def __init__(self, delay="1s"):
        self.delay = delay


class TxInfo:
    def __init__(self, frequency=868100000, modulation=Modulation()):
        self.frequency = frequency
        self.modulation = modulation


    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
