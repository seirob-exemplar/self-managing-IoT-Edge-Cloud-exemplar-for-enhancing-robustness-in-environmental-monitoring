import json

from enums.crc_status_enum import CRCStatusEnum


class RxInfo:
    def __init__(self, gateway_id="", time="", rssi=-60, lo_ra_snr=7, context="", uplink_id=""):
        self.gatewayId = gateway_id  # encoded base64 standard
        self.uplinkId = uplink_id
        self.time = time  # set only when there is a GPS time source
        self.rssi = rssi
        self.snr = lo_ra_snr
        self.context = context

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
