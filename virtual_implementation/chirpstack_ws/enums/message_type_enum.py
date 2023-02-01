from enum import Enum


# Message types
class MessageTypeEnum(Enum):
    JOIN_REQUEST = (0, "JoinRequest", False)
    JOIN_ACCEPT = (1, "JoinAccept", True)
    UNCONFIRMED_DATA_UP = (2, "UnconfirmedDataUp", True)
    UNCONFIRMED_DATA_DOWN = (3, "UnconfirmedDataDown", False)
    CONFIRMED_DATA_UP = (4, "ConfirmedDataUp", True)
    CONFIRMED_DATA_DOWN = (5, "ConfirmedDataDown", False)

    def get_key(self):
        return self.value[0]

    def get_name(self):
        return self.value[1]

    def is_uplink(self):
        return self.value[2]

    @staticmethod
    def find_by_key(key):
        for message_type in MessageTypeEnum:
            if message_type.get_key() == key:
                return message_type
        return None

    @staticmethod
    def find_by_name(name):
        for message_type in MessageTypeEnum:
            if message_type.get_name() == name:
                return message_type
        return None
