import json


class PacketsPerFrequency:
    def __init__(self):
        self
        # self.d = {}
        # for i in range(0, len(args), 2):
        #     self.d[args[i]] = args[i+1]

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)