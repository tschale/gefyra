from decouple import config


class OperatorConfiguration:
    def __init__(self):
        self.NAMESPACE = config("NAMESPACE", default="default")
        self.STOWAWY_IMAGE = config("GEFYRA_STOWAWAY_IMAGE", default="quay.io/gefyra/stowaway")
        self.STOWAWY_TAG = config("GEFYRA_STOWAWAY_TAG", default="latest")
        self.WIREGUARD_EXT_PORT = config("GEFYRA_STOWAWAY_SERVERPORT", cast=int, default=31820)
        self.STOWAWAY_PGID = config("GEFYRA_STOWAWAY_PGID", default="1000")
        self.STOWAWAY_PUID = config("GEFYRA_STOWAWAY_PUID", default="1000")
        self.STOWAWAY_STARTUP_TIMEOUT = config("GEFYRA_STOWAWAY_STARTUP_TIMEOUT", cast=int, default=60)
        self.STOWAWAY_PEER_DNS = config("GEFYRA_STOWAWAY_PUID", default="auto")
        self.STOWAWAY_PEER_CONFIG_PATH = config("GEFYRA_STOWAWAY_PEER_CONFIG_PATH",
                                                default="/config/peer1/peer1.conf")
        self.STOWAWAY_INTERNAL_SUBNET = config("GEFYRA_INTERNAL_SUBNET", default="192.168.99.0")


    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items() if k.isupper()
        }

    def __str__(self):
        return str(self.to_dict())


configuration = OperatorConfiguration()