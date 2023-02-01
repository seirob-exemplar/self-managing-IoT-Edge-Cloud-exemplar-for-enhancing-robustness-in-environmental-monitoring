from enum import Enum


class MajorTypeEnum(Enum):
    LoRaWANR1 = (0, "LoRaWANR1")
    LoRaWANR0 = (1, "LoRaWANR0")

    def get_key(self):
        return self.value[0]

    def get_name(self):
        return self.value[1]

    @staticmethod
    def find_by_key(key):
        for major_type in MajorTypeEnum:
            if major_type.get_key() == key:
                return major_type
        return None

    @staticmethod
    def find_by_name(name):
        for major_type in MajorTypeEnum:
            if major_type.get_name() == name:
                return major_type
        return None
