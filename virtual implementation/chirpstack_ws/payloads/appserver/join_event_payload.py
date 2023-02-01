import json

from payloads.info.rx_info import RxInfo
from payloads.info.tx_info import TxInfo


class JoinEventPayload:
    def __init__(self, application_id="", device_name="", dev_eui="", dev_addr="", rx_info=RxInfo(), tx_info=TxInfo(),
                 dr=0, published_at=""):
        self.applicationID = application_id
        self.deviceName = device_name
        self.devEUI = dev_eui
        self.devAddr = dev_addr
        self.rxInfo = rx_info
        self.txInfo = tx_info
        self.dr = dr
        self.publishedAt = published_at

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
