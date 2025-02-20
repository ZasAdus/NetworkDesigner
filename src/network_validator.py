from ipaddress import IPv4Address

class NetworkValidator:
    @staticmethod
    def validate_ip_address(ip):
        if ip == "":
            return True
        try:
            IPv4Address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_subnet_mask(mask):
        if mask == "":
            return True
        try:
            return 1 <= int(mask) <= 32
        except ValueError:
            return False


    @staticmethod
    def validate_vlan(vlan):
        if vlan == "":
            return True
        try:
            return 1 <= int(vlan) <= 4094
        except ValueError:
            return False