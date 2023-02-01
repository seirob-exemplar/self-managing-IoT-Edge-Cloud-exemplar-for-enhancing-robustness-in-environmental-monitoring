from enum import Enum


class MacCommandEnum(Enum):
    LINK_ADR_REQ = (3, "LinkADRReq", False, 4)
    LINK_ADR_ANS = (3, "LinkADRAns", True, 1)
    DEVICE_STATUS_REQ = (6, "DeviceStatusReq", False, 0) #dovrebbe essere dev forse
    DEVICE_STATUS_ANS = (6, "DeviceStatusAns", True, 2)
    NEW_CHANNEL_REQ = (7, "NewChannelReq", False, 5)
    NEW_CHANNEL_ANS = (7, "NewChannelAns", True, 1)


    def get_key(self):
        return self.value[0]

    def get_name(self):
        return self.value[1]

    def is_uplink(self):
        return self.value[2]

    def get_payload_lenght(self):
        return self.value[3]

    @staticmethod
    def find_by_key(key, is_uplink):
        for mac_command in MacCommandEnum:
            if mac_command.get_key() == key and mac_command.is_uplink() == is_uplink:
                return mac_command
        return None

    @staticmethod
    def find_by_name(name, is_uplink):
        for mac_command in MacCommandEnum:
            if mac_command.get_name() == name and mac_command.is_uplink() == is_uplink:
                return mac_command
        return None
