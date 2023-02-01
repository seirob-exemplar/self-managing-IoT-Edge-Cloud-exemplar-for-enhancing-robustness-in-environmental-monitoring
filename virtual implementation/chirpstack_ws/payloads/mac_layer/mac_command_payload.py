import json


class MacCommandPayload:
    def __init__(self, battery=None, margin=None, ch_index=None, freq=None, max_dr=None, min_dr=None):
        # DevStatusAns
        self.battery = battery
        self.margin = margin
        # NewChannelReq
        self.chIndex = ch_index
        self.freq = freq
        self.maxDR = max_dr
        self.minDR = min_dr

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class MacCommandItem:
    def __init__(self, cid=None, payload=None):
        self.cid = cid
        self.payload = payload

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
