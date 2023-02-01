import json

from payloads.info.rx_info import RxInfo
from payloads.info.tx_info import TxInfo


class UpPayload:
    def __init__(self, phy_payload="", tx_info=TxInfo(), rx_info=RxInfo()):
        self.phyPayload = phy_payload
        self.txInfo = tx_info
        self.rxInfo = rx_info

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
