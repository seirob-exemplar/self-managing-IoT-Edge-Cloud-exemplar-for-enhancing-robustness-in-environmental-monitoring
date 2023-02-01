from enum import Enum


class CRCStatusEnum(Enum):
    NO_CRC = 0
    BAD_CRC = 1
    CRC_OK = 2
