import base64
import struct

from Crypto.Cipher import AES

from enums.bcolors import BColors
from enums.mac_command_enum import MacCommandEnum
from enums.major_type_enum import MajorTypeEnum
from enums.message_type_enum import MessageTypeEnum
from payloads.mac_layer.join_accept_mac_payload import JoinAccpetMacPayload
from payloads.mac_layer.mac_command_payload import MacCommandItem, MacCommandPayload
from payloads.mac_layer.phy_payload import FCTRL, Frame, FHDR, PhyPayload, MacPayload, MHDR
from utils.payload_util import encrypt_frm_payload, encrypt_mac_payload


def get_mtype(byte):
    return struct.unpack("B", byte)[0] >> 5


def get_major(byte):
    return struct.unpack("B", byte)[0] & 0x03


def decode_net_id(data):
    return data[::-1]


def decode_dev_addr(data):
    return data[::-1]


def decode_mic(data):
    return data[::-1]


def decode_fhdr(data):
    fhdr = FHDR()
    fhdr.devAddr = decode_dev_addr(data[0:4]).hex()
    fhdr.fCtrl = FCTRL(data[4:5])
    f_cnt_byte = data[5:7]
    f_cnt_byte += bytearray(2)
    fhdr.fCnt = int.from_bytes(f_cnt_byte, 'little')
    if len(data) > 7:
        fhdr.fOpts = []
        fhdr.fOpts.append(Frame(base64.b64encode(data[7:])))
    return fhdr


def encode_dev_addr(data):
    return data[::+1]


def encode_fhdr(fhdr):
    byte = bytearray()
    byte += encode_dev_addr(int(fhdr.devAddr, 16).to_bytes(4, 'little'))
    byte += fhdr.fCtrl.get_byte()
    byte += fhdr.fCnt.to_bytes(2, 'little')
    return byte


def get_command_payload(command_type, data):
    mac_command_payload = MacCommandPayload()
    if command_type == MacCommandEnum.DEVICE_STATUS_ANS:
        mac_command_payload.battery = data[0]
        if data[1] > 31:
            mac_command_payload.margin = data[1] - 64
        else:
            mac_command_payload.margin = data[1]
    elif command_type == MacCommandEnum.NEW_CHANNEL_REQ:
        mac_command_payload.chIndex = data[0]
        mac_command_payload.freq = int.from_bytes(data[1:4], 'little') * 100
        mac_command_payload.maxDR = data[4] & ((1 << 3) ^ (1 << 2) ^ (1 << 1) ^ (1 << 0))
        mac_command_payload.minDR = (data[4] & ((1 << 7) ^ (1 << 6) ^ (1 << 5) ^ (1 << 4))) >> 4

    return mac_command_payload


def decode_data_payload_to_mac_commands(is_uplink, frames):
    if len(frames) == 0:
        return []

    if len(frames) != 1:
        raise Exception("lorawan: exactly one Payload expected")

    data = frames[0]

    mac_command_payload_list = []
    i = 0
    while i < len(data):
        mac_command_payload = MacCommandItem()
        command_type = MacCommandEnum.find_by_key(data[i], is_uplink)
        #print(data[i]) #mac command
        if command_type is None:
            raise Exception("Unknown mac command")
        payload_lenght = command_type.get_payload_lenght()
        mac_command_payload.cid = command_type.get_name()
        mac_command_payload.payload = get_command_payload(command_type, data[i + 1:i + 1 + payload_lenght])
        mac_command_payload_list.append(mac_command_payload)
        i = i + 1 + payload_lenght

    return mac_command_payload_list


def encode_mac_payload(cid, mac_command):
    b = bytearray(cid.get_payload_lenght() + 1)
    b[0] = cid.get_key()
    mac_command_payload = mac_command.payload
    if cid == MacCommandEnum.DEVICE_STATUS_REQ:
        pass
    elif cid == MacCommandEnum.DEVICE_STATUS_ANS:
        if mac_command_payload.margin < -32:
            raise Exception("lorawan: min value of Margin is -32")
        if mac_command_payload.margin > 31:
            raise Exception("lorawan: max value of Margin is 31")
        b[1] = mac_command_payload.battery
        if mac_command_payload.margin < 0:
            b[2] = 64 + mac_command_payload.margin
        else:
            b[2] = mac_command_payload.margin
    elif cid == MacCommandEnum.NEW_CHANNEL_REQ:
        if mac_command_payload.freq / 100 >= 16777216:
            raise Exception("lorawan: max value of Freq is 2^24 - 1")
        if mac_command_payload.freq % 100 != 0:
            raise Exception("lorawan: Freq must be a multiple of 100")
        if mac_command_payload.maxDR > 15:
            raise Exception("lorawan: max value of MaxDR is 15")
        if mac_command_payload.minDR > 15:
            raise Exception("lorawan: max value of MinDR is 15")

        b[1] = mac_command_payload.chIndex
        b[2:5] = int(mac_command_payload.freq / 100).to_bytes(3, 'little')
        b[5] = mac_command_payload.minDR ^ (mac_command_payload.maxDR << 4)
    else:
        raise Exception("Not managed command type")

    return b


def encode_mac_commands_to_data_payload(is_uplink, mac_commands):
    data = bytearray()
    for mac_command in mac_commands:
        cid = MacCommandEnum.find_by_name(mac_command.cid, is_uplink)
        if cid is None:
            raise Exception("Unknown command ")
        mac_payload_encoded = encode_mac_payload(cid, mac_command)
        data += mac_payload_encoded

    return data


# functions

def decode_join_accept_mac_payload(app_key, dev_nonce, phy_payload):
    join_accept_mac_payload = JoinAccpetMacPayload()
    mac_payload_byte_encrypted = base64.b64decode(phy_payload.macPayload.bytes)
    mic_encrypted = bytes.fromhex(phy_payload.mic)
    key = bytes.fromhex(app_key)
    mac_payload_byte = encrypt_mac_payload(app_key, mac_payload_byte_encrypted, mic_encrypted)

    join_accept_mac_payload.app_nonce = int.from_bytes(mac_payload_byte[0:3], 'little')
    join_accept_mac_payload.net_ID = decode_net_id(mac_payload_byte[3:6]).hex()
    join_accept_mac_payload.dev_addr = decode_dev_addr(mac_payload_byte[6:10]).hex()
    join_accept_mac_payload.DL_settings = mac_payload_byte[10:11].hex()
    join_accept_mac_payload.rx_delay = mac_payload_byte[11]
    join_accept_mac_payload.CF_list = base64.b64encode(mac_payload_byte[12:]).decode()

    # computing network e app sessione keys

    n = bytearray(16)
    a = bytearray(16)
    n[0] = 1
    n[1:4] = mac_payload_byte[0:3]
    n[4:7] = mac_payload_byte[3:6]
    n[7:9] = dev_nonce.to_bytes(2, 'little')
    a[0] = 2
    a[1:4] = mac_payload_byte[0:3]
    a[4:7] = mac_payload_byte[3:6]
    a[7:9] = dev_nonce.to_bytes(2, 'little')

    cipher = AES.new(key, AES.MODE_ECB)
    join_accept_mac_payload.nwk_SKey = cipher.encrypt(n).hex()
    join_accept_mac_payload.app_SKey = cipher.encrypt(a).hex()
    return join_accept_mac_payload


def decode_fopts_payload_to_mac_commands(is_uplink, frames):
    data = []
    if frames is None or len(frames) <= 0:
        return data
    for frame in frames:
        data.append(base64.b64decode(frame.bytes))
    return decode_data_payload_to_mac_commands(is_uplink, data)


def decode_frm_payload_to_mac_commands(app_skey, net_skey, f_port, is_uplink, dev_addr, f_cnt, frames):
    data = []
    if frames is None or len(frames) <= 0:
        return data
    if f_port is None or f_port > 0:
        return data
    for frame in frames:
        data.append(bytearray(base64.b64decode(frame.bytes)))

    dev_addr_byte = encode_dev_addr(int(dev_addr, 16).to_bytes(4, 'little'))

    encrypted_data = []
    for d in data:
        encrypted_data.append(encrypt_frm_payload(app_skey, net_skey, f_port, is_uplink, dev_addr_byte, f_cnt, d))

    return decode_data_payload_to_mac_commands(is_uplink, encrypted_data)


def encode_mac_commands_to_frm_payload(app_skey, net_skey, f_port, is_uplink, dev_addr, f_cnt, mac_commands):
    data = encode_mac_commands_to_data_payload(is_uplink, mac_commands)

    dev_addr_byte = encode_dev_addr(int(dev_addr, 16).to_bytes(4, 'little'))
    encrypted_data = encrypt_frm_payload(app_skey, net_skey, f_port, is_uplink, dev_addr_byte, f_cnt, data)

    return base64.b64encode(encrypted_data).decode()


def decode_phy_payload(phy_payload_encoded):
    data = base64.b64decode(phy_payload_encoded)

    phy_payload = PhyPayload()
    mhdr_byte = data[0].to_bytes(1, 'big')
    mac_payload_byte = data[1:-4] # estraggo un sottovettore
    mic = data[-4:] # ultime 4 celle del vettore
    assert (len(data) == len(mhdr_byte) + len(mac_payload_byte) + len(mic))

    mtype_key = get_mtype(mhdr_byte)
    major_key = get_major(mhdr_byte)
    mtype = MessageTypeEnum.find_by_key(mtype_key)
    major = MajorTypeEnum.find_by_key(major_key)

    phy_payload.mhdr = MHDR()

    if major != MajorTypeEnum.LoRaWANR1:
        raise Exception("Lorawan version must be 1.0 or 1.1")

    phy_payload.mhdr.major = major.get_name()

    if mtype == MessageTypeEnum.JOIN_REQUEST:
        # print(" *** Join-request")
        join_eui = data[1:9]
        dev_eui = data[9:17]
        nonce = data[17:19]

        phy_payload.macPayload = MacPayload()
        join_eui = join_eui[::-1]
        dev_eui = dev_eui[::-1]
        nonce = nonce[::-1]
        phy_payload.mhdr.mType = mtype.get_name()
        phy_payload.macPayload.joinEUI = join_eui.hex()
        phy_payload.macPayload.devEUI = dev_eui.hex()
        phy_payload.macPayload.devNonce = int.from_bytes(nonce, 'big')
        phy_payload.mic = mic.hex()
        # print("  JoinEUI: %s" % join_eui.hex())
        # print("  DevEUI: %s" % dev_eui.hex())
        # print("  Nonce:  %s" % nonce.hex())
        # print("  MIC: %s" % mic.hex())
    elif mtype == MessageTypeEnum.JOIN_ACCEPT:
        # print(" *** Join Accept")
        phy_payload.mhdr.mType = mtype.get_name()
        phy_payload.macPayload = MacPayload()
        phy_payload.macPayload.bytes = base64.b64encode(mac_payload_byte).decode()
        phy_payload.mic = mic.hex()
        #devAddr = mac_payload_byte[6:10]
        #devAddr = devAddr[::-1]
        #devAddr = devAddr.hex()
        #print(len(data))
        # print("  Data base64 encoded: %s" % base64.b64encode(macPayloadByte))
    elif mtype in (MessageTypeEnum.CONFIRMED_DATA_UP, MessageTypeEnum.CONFIRMED_DATA_DOWN,
                   MessageTypeEnum.UNCONFIRMED_DATA_UP, MessageTypeEnum.UNCONFIRMED_DATA_DOWN):
        phy_payload.mhdr.mType = mtype.get_name()
        data_len = len(mac_payload_byte)
        mac_payload = MacPayload()

        if data_len < 7:
            raise Exception("lorawan: at least 7 bytes needed to decode FHDR")
        f_ctrl = FCTRL(mac_payload_byte[4:5])

        if data_len < 7 + f_ctrl.fOptsLen:
            raise Exception("lorawan: not enough bytes to decode FHDR")
        mac_payload.fhdr = decode_fhdr(mac_payload_byte[0:7 + f_ctrl.fOptsLen])

        if data_len > 7 + f_ctrl.fOptsLen:
            mac_payload.fPort = mac_payload_byte[7 + f_ctrl.fOptsLen]

        if len(mac_payload_byte[7 + mac_payload.fhdr.fCtrl.fOptsLen + 1:]) > 0:
            if mac_payload.fPort is not None and mac_payload.fPort == 0 and f_ctrl.fOptsLen > 0:
                raise Exception("lorawan: FPort must not be 0 when FOpts are set")
            frame_bytes = base64.b64encode(mac_payload_byte[7 + mac_payload.fhdr.fCtrl.fOptsLen + 1:])
            mac_payload.frmPayload.append(Frame(frame_bytes))

        phy_payload.macPayload = mac_payload
        phy_payload.mic = mic.hex()

        # print(" *** ", mtype.get_name())

        # print("  DevAddr: %08s  " % phy_payload.macPayload.fhdr.devAddr)
        # print("  fCtrl: %02s" % phy_payload.macPayload.fhdr.fCtrl.get_string())
        # print("  f_cnt: %05d   f_port: %01x" % (phy_payload.macPayload.fhdr.fCnt, phy_payload.macPayload.fPort))
        # if len(phy_payload.macPayload.frmPayload) > 0:
        # print("  FRMPayload: %04s " % phy_payload.macPayload.frmPayload[0].bytes)
        # print("  mic: %04s " % phy_payload.mic)
    else:
        print(f"{BColors.WARNING.value}Unsupported type{BColors.ENDC.value}")
    return phy_payload


def encode_phy_payload(phy_payload):
    mtype = MessageTypeEnum.find_by_name(phy_payload.mhdr.mType)
    data = bytearray()

    if mtype == MessageTypeEnum.JOIN_REQUEST:
        join_eui = int(phy_payload.macPayload.joinEUI, 16).to_bytes(8, 'big')
        dev_eui = int(phy_payload.macPayload.devEUI, 16).to_bytes(8, 'big')
        nonce = phy_payload.macPayload.devNonce.to_bytes(2, 'big')

        data += (mtype.get_key() << 5).to_bytes(1, 'big')
        join_eui = join_eui[::-1]
        dev_eui = dev_eui[::-1]
        nonce = nonce[::-1]
        data += join_eui
        data += dev_eui
        data += nonce
        data += int(phy_payload.mic, 16).to_bytes(4, 'big')
        return base64.b64encode(data).decode()
    if mtype == MessageTypeEnum.JOIN_ACCEPT:
        data += (mtype.get_key() << 5).to_bytes(1, 'big')
        data += base64.b64decode(phy_payload.macPayload.bytes.encode())
        data += int(phy_payload.mic, 16).to_bytes(4, 'big')
        return base64.b64encode(data).decode()
    if mtype in (MessageTypeEnum.CONFIRMED_DATA_UP, MessageTypeEnum.CONFIRMED_DATA_DOWN,
                 MessageTypeEnum.UNCONFIRMED_DATA_UP, MessageTypeEnum.UNCONFIRMED_DATA_DOWN):

        data += (mtype.get_key() << 5).to_bytes(1, 'big')

        data += encode_fhdr(phy_payload.macPayload.fhdr)
        data += int(phy_payload.macPayload.fPort).to_bytes(1, 'big')

        frm_payload = phy_payload.macPayload.frmPayload
        for frame in frm_payload:
            data += base64.b64decode(frame.bytes.encode())

        data += int(phy_payload.mic, 16).to_bytes(4, 'big')

        return base64.b64encode(data).decode()

    print(f"{BColors.WARNING.value}Unsupported type{BColors.ENDC.value}")
    return None


def encode_phy_payload_from_json(json_packet):
    return encode_phy_payload(get_phy_payload_from_json(json_packet))


def get_phy_payload_from_json(json_packet):
    p = PhyPayload()
    p.mhdr.mType = json_packet['mhdr']['mType']
    p.mhdr.major = json_packet['mhdr']['major']
    if p.mhdr.mType == MessageTypeEnum.JOIN_REQUEST.get_name():
        p.macPayload.joinEUI = json_packet['macPayload']['joinEUI']
        p.macPayload.devEUI = json_packet['macPayload']['devEUI']
        p.macPayload.devNonce = json_packet['macPayload']['devNonce']
    elif p.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.get_name():
        p.macPayload.bytes = json_packet['macPayload']['bytes']
    else:
        p.macPayload.fhdr.devAddr = json_packet['macPayload']['fhdr']['devAddr']
        p.macPayload.fhdr.fCtrl.adr = json_packet['macPayload']['fhdr']['fCtrl']['adr']
        p.macPayload.fhdr.fCtrl.adrAckReq = json_packet['macPayload']['fhdr']['fCtrl']['adrAckReq']
        p.macPayload.fhdr.fCtrl.ack = json_packet['macPayload']['fhdr']['fCtrl']['ack']
        p.macPayload.fhdr.fCtrl.fPending = json_packet['macPayload']['fhdr']['fCtrl']['fPending']
        p.macPayload.fhdr.fCtrl.classB = json_packet['macPayload']['fhdr']['fCtrl']['classB']
        p.macPayload.fhdr.fCnt = json_packet['macPayload']['fhdr']['fCnt']
        p.macPayload.fPort = json_packet['macPayload']['fPort']
        if json_packet['macPayload']['frmPayload'] is not None:
            for bytes_data in json_packet['macPayload']['frmPayload']:
                p.macPayload.frmPayload.append(Frame(bytes_data['bytes']))
    p.mic = json_packet['mic']
    return p
