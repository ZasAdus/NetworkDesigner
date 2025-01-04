import random
from database import Database


class MAC:
    def __init__(self):
        self.address = self.generate_mac()

    def generate_mac(self):
        mac = [random.randint(0x00, 0xFF) for _ in range(6)]
        return ':'.join(f'{octet:02x}' for octet in mac) if mac else None

    @staticmethod
    def generate_unique_mac(device_type=None, device_id=None):
        address = MAC().generate_mac()
        while Database.mac_exists(address) or not address:
            address = MAC().generate_mac()
        return address

    def get_address(self):
        return self.address