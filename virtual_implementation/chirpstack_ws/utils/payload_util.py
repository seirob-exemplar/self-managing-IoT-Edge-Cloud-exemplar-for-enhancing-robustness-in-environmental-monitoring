import json
from typing import TypeVar

from Crypto.Cipher import AES
from Crypto.Hash import CMAC

from enums.lorawan_version_enum import LorawanVersionEnum

T = TypeVar('T')


def encrypt_frm_payload(app_skey, net_skey, f_port, is_uplink, dev_addr_byte, f_cnt, data):
    if f_port == 0:
        key = bytes.fromhex(net_skey)
    else:
        key = bytes.fromhex(app_skey)

    p_len = len(data)
    if p_len % 16 != 0:
        data += bytearray(16 - (p_len % 16))

    cipher = AES.new(key, AES.MODE_ECB)

    a = bytearray(16)
    a[0] = 0x01
    if not is_uplink:
        a[5] = 0x01

    a[6:10] = dev_addr_byte
    temp = f_cnt.to_bytes(2, 'little') #2,little
    temp += bytearray(2)
    a[10:14] = temp

    i = 0
    while i < len(data) / 16:
        a[15] = int(i + 1)

        s = cipher.encrypt(a)

        j = 0
        while j < len(s):
            data[i * 16 + j] = int(data[i * 16 + j]) ^ (s[j])
            j += 1

        i += 1

    return data[0:p_len]


def encrypt_mac_payload(app_key, mac_payload, mic):
    key = bytes.fromhex(app_key)
    ciphertext = bytearray()
    ciphertext += mac_payload
    ciphertext += mic

    if len(ciphertext) % 16 != 0:
        raise Exception("lorawan: plaintext must be a multiple of 16 bytes")

    cipher = AES.new(key, AES.MODE_ECB)

    text = bytearray(len(ciphertext))
    i = 0
    while i < len(ciphertext) / 16:
        offset = i * 16
        text[offset: offset + 16] = cipher.encrypt(ciphertext[offset:offset + 16])
        i += 1

    # phy_payload.mic = text[-4:].hex()
    return text[0:-4]


def compute_join_accept_mic(phy_payload, app_key):
    key = bytes.fromhex(app_key)
    mic = bytearray(4)
    mhdr = phy_payload[0:1]
    mac_payload = encrypt_mac_payload(app_key, phy_payload[1:-4], phy_payload[-4:])
    mic_bytes = bytearray()
    mic_bytes += mhdr
    mic_bytes += mac_payload

    ap_mic = CMAC.new(key, ciphermod=AES)
    ap_mic.update(mic_bytes)

    mic[:] = ap_mic.digest()[0:4]

    text = bytearray()
    text += mac_payload
    text += mic

    if len(text) % 16 != 0:
        raise Exception("lorawan: plaintext must be a multiple of 16 bytes")

    cipher = AES.new(key, AES.MODE_ECB)

    ciphertext = bytearray(len(text))
    i = 0
    while i < len(ciphertext) / 16:
        offset = i * 16
        ciphertext[offset: offset + 16] = cipher.decrypt(text[offset:offset + 16])
        i += 1

    mic_enc = ciphertext[-4:]
    return mic_enc.hex()


def compute_join_request_mic(phy_payload, app_key):
    key = bytes.fromhex(app_key)
    mic = bytearray(4)
    mhdr = phy_payload[0:1]
    mac_payload = phy_payload[1:-4]

    mic_bytes = bytearray()
    mic_bytes += mhdr
    mic_bytes += mac_payload

    ap_mic = CMAC.new(key, ciphermod=AES)
    ap_mic.update(mic_bytes)
    mic[:] = ap_mic.digest()[0:4]

    return mic.hex()


def compute_data_mic(phy_payload, mac_version, conf_f_cnt, tx_dr, tx_ch, f_nwk_s_int_key, is_uplink):
    mic = bytearray(4)
    key = bytes.fromhex(f_nwk_s_int_key)
    mhdr = phy_payload[0:1]
    mac_payload = phy_payload[1:-4]
    fhdr = mac_payload[0:7]

    # confFCnt set to 0 when there are no ack
    if (int.from_bytes(fhdr[4:5], 'big') & 0x20) != 0:
        conf_f_cnt = 0

    conf_f_cnt = conf_f_cnt % (1 << 16)

    mic_bytes = bytearray()
    mic_bytes += mhdr
    mic_bytes += mac_payload

    b0 = bytearray(16)
    b1 = bytearray(16)

    b0[0] = 0x49
    b1[0] = 0x49

    if not is_uplink:
        b0[5] = 0x01

    fhdr = mac_payload[0:7]
    dev_adress_byte = fhdr[0:4]

    # dev_addr
    b0[6:10] = dev_adress_byte
    b1[6:10] = dev_adress_byte

    # fcntup
    temp = fhdr[5:7]
    temp += bytearray(2)
    b0[10:14] = temp
    b1[10:14] = temp

    b0[15] = len(mic_bytes)
    b1[15] = len(mic_bytes)

    # set up remaining bytes
    b1[1:3] = conf_f_cnt.to_bytes(2, 'little')
    b1[3] = tx_dr
    b1[4] = tx_ch

    fn_mic = CMAC.new(key, ciphermod=AES)

    b0 += mic_bytes
    fn_mic.update(b0)

    if mac_version == LorawanVersionEnum.LoRaWANR1_0.value:
        mic[:] = fn_mic.digest()[0:4]

    return mic.hex()


def get_json_from_object(obj: T):
    json_str_object = json.dumps(obj.to_json())
    json_object = json.loads(json_str_object)

    def remove_nulls(d):
        return {k: v for k, v in d.items() if v is not None}

    return json.loads(json_object, object_hook=remove_nulls)
