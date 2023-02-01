from enum import Enum


class TxAckStatusEnum(Enum):
    IGNORED = 0
    OK = 1
    TOO_LATE = 2
    TOO_EARLY = 3
    COLLISION_PACKET = 4
    COLLISION_BEACON = 5
    TX_FREQ = 6
    TX_POWER = 7
    GPS_UNLOCKED = 8
    QUEUE_FULL = 9
    INTERNAL_ERROR = 10
