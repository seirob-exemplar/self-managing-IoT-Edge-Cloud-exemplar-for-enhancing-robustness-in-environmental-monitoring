import json

from payloads.info.packets_per_frequency import PacketsPerFrequency
from payloads.info.packets_per_status import PacketsPerStatus
from payloads.info.packets_per_modulation import PacketsPerModulation
from payloads.info.packets_per_modulation import PacketsPerModulation

class Metadata:
    def __init__(self):
        self

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class StatsPayload:
    def __init__(self, id_gateway="", time="", rx_packets_received=1, rx_packets_received_ok=1,
                 tx_packets_received=1, tx_packets_emitted=1,
                 tx_packets_per_frequency=PacketsPerFrequency(), rx_packets_per_frequency=PacketsPerFrequency(),
                 tx_packets_per_modulation=PacketsPerModulation(), rx_packets_per_modulation=PacketsPerModulation(),
                 tx_packets_per_status=PacketsPerStatus()):
                 
        self.gatewayId = id_gateway 
        self.time = time  # format datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.rxPacketsReceived = rx_packets_received
        self.rxPacketsReceivedOk = rx_packets_received_ok
        self.txPacketsReceived = tx_packets_received
        self.txPacketsEmitted = tx_packets_emitted

        self.txPacketsPerFrequency = tx_packets_per_frequency
        self.rxPacketsPerFrequency = rx_packets_per_frequency

        self.txPacketsPerModulation = [tx_packets_per_modulation]
        #self.txPacketsPerModulation.append()
        self.rxPacketsPerModulation = [rx_packets_per_modulation]
        #self.rxPacketsPerModulation.append()
        self.txPacketsPerStatus = tx_packets_per_status


    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
