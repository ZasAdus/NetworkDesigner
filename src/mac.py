import random
from database import Database


class MAC:
    def __init__(self):
        self.address = None

    @staticmethod
    def _format_mac_address(address):
        return ':'.join(f'{x:02x}' for x in address)

    @staticmethod
    def generate_unique_mac(device_type=None, device_id=None):
        while True:
            address = [random.randint(0x00, 0xFF) for _ in range(6)]
            if not address:
                continue

            mac_str = MAC._format_mac_address(address)
            if not Database.mac_exists(mac_str):
                return mac_str

    def get_address(self):
        return self.address