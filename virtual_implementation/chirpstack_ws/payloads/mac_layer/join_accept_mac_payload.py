import json


class JoinAccpetMacPayload:
    def __init__(self, app_nonce=None, net_id=None, dev_addr=None, dl_settings=None, rx_delay=None, cf_list=None,
                 nwk_s_key=None, app_s_key=""):
        self.app_nonce = app_nonce
        self.net_ID = net_id
        self.dev_addr = dev_addr
        self.DL_settings = dl_settings
        self.rx_delay = rx_delay
        self.CF_list = cf_list
        self.nwk_SKey = nwk_s_key
        self.app_SKey = app_s_key

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
