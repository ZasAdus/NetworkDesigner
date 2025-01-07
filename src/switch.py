from mac import MAC as mac
from database import Database

class Switch:
    def __init__(self,  x, y, number_of_ports=8):
        self.number_of_ports = number_of_ports
        self.device_type = 'switch'
        self.x = x
        self.y = y
        self.device_id = Database.get_next_device_id()
        self.interfaces = {}

        mac_address = mac.generate_unique_mac('switch', self.device_id)
        Database.insert_device(self.device_id, mac_address, 'switch', x, y)

        for port in range(1, number_of_ports + 1):
            port_mac = mac.generate_unique_mac(None, self.device_id)
            self.interfaces[port] = {
                'mac': port_mac,
                'vlans': None,
                'port_type': None,
            }
            Database.insert_port_switch(self.device_id, port, port_mac)

    def set_interface_switch(self, port, vlans, port_type):
        if port in self.interfaces:
            self.interfaces[port]['vlans'] = vlans
            self.interfaces[port]['port_type'] = port_type

            vlan_str = ','.join(map(str, vlans))
            Database.update_port_switch(
                self.device_id,
                port,
                vlan_str,
                port_type
            )
            return True
        return False
