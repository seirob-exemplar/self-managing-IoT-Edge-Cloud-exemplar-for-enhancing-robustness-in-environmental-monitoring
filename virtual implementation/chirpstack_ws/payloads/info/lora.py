import json


class Lora:
    def __init__(self, bandwidth=125000, spreading_factor=7, code_rate="CR_4_5", polarization_inversion=True):
        self.bandwidth = bandwidth
        self.spreadingFactor = spreading_factor
        self.codeRate = code_rate
        self.polarizationInversion = polarization_inversion

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
