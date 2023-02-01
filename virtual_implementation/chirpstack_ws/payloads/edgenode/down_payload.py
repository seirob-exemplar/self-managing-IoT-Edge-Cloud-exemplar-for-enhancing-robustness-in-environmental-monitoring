import json

from payloads.info.tx_info import TxInfo


class DownItem:
    def __init__(self, phy_payload="", tx_info=TxInfo()):
        self.phyPayload = phy_payload
        self.txInfo = tx_info

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class DownPayload:
    def __init__(self, phy_payload="", tx_info=TxInfo(), token=None, downlink_id="", items=[], gateway_id=""):
        self.phyPayload = phy_payload
        self.txInfo = tx_info
        self.token = token
        self.downlinkID = downlink_id
        self.items = items  # list of DownItem
        self.gatewayID = gateway_id

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
