import ipaddress as ip
from mac import MAC as mac
from database import Database

class Computer:
    def __init__(self, x, y):
        self.device_type = 'computer'
        self.x = x
        self.y = y
        self.device_id = Database.get_next_device_id()

        mac_address = mac.generate_unique_mac('computer', self.device_id)
        Database.insert_device(self.device_id, mac_address, 'computer', x, y)

        port = mac.generate_unique_mac(None, self.device_id)
        Database.insert_port_computer(self.device_id, port)


    def set_interface_computer(self, ip_address, subnet_mask):
        try:
            ip_interface = ip.ip_interface(f"{ip_address}/{subnet_mask}")
            Database.update_port_computer(
                self.device_id,
                ip_address=str(ip_interface.ip),
                subnet_mask=subnet_mask
            )
            return True
        except ValueError:
            return False