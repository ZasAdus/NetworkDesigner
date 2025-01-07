from mac import MAC as mac
import ipaddress as ip
from database import Database

class Router:
    def __init__(self, x, y, number_of_ports=4):
        self.number_of_ports = number_of_ports
        self.device_type = 'router'
        self.x = x
        self.y = y
        self.device_id = Database.get_next_device_id()
        self.interfaces = {}

        mac_address = mac.generate_unique_mac('router', self.device_id)
        Database.insert_device(self.device_id, mac_address, 'router', x, y)

        for port in range(1, number_of_ports + 1):
            port_mac = mac.generate_unique_mac(None, self.device_id)
            self.interfaces[port] = {
                'mac': port_mac,
                'ip_address': None,
                'subnet_mask': None,
                'vlans': [],
                'enabled': True
            }
            Database.insert_port_router(self.device_id, port, port_mac)

    def set_interface_router(self, port, ip_address, subnet_mask, vlan_id=None):
        if port in self.interfaces:
            try:
                ip_interface = ip.ip_interface(f"{ip_address}/{subnet_mask}")

                self.interfaces[port]['ip_address'] = str(ip_interface.ip)
                self.interfaces[port]['subnet_mask'] = subnet_mask
                if vlan_id:
                    self.interfaces[port]['vlans'] = [vlan_id]

                Database.update_port_router(
                    device_id=self.device_id,
                    port_number=port,
                    ip_address=str(ip_interface.ip),
                    subnet_mask=subnet_mask,
                    vlan=vlan_id
                )
                return True
            except ValueError:
                return False
        return False