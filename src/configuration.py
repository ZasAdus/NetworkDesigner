from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QMessageBox, QGridLayout,
                             QSpinBox, QTabWidget, QWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from database import Database


class PortInfoTab(QWidget):
    def __init__(self, device_instance):
        super().__init__()
        self.device_instance = device_instance
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Port", "Connected To", "MAC Address", "Configuration"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.populate_port_info()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def populate_port_info(self):
        device_id = self.device_instance.device_id
        device_type = self.device_instance.device_type
        connections = Database.get_device_connections(device_id)
        if device_type == "computer":
            self.populate_computer_ports(connections)
        elif device_type == "router":
            self.populate_router_ports(connections)
        elif device_type == "switch":
            self.populate_switch_ports(connections)

    def get_device_info(self, device_id):
        return Database.cursor.execute(
            "SELECT device_type FROM devices WHERE device_id = ?",
            (device_id,)
        ).fetchone()[0]

    def populate_computer_ports(self, connections):
        self.table.setRowCount(1)
        port_info = Database.cursor.execute(
            "SELECT mac_address, ip_address, subnet_mask FROM computer_ports WHERE device_id = ?",
            (self.device_instance.device_id,)
        ).fetchone()

        if port_info:
            mac, ip, subnet = port_info
            config_str = f"IP: {ip if ip else 'Not set'}\nSubnet: {subnet if subnet else 'Not set'}"
        else:
            mac, config_str = "N/A", "Not configured"

        connected_to = "Not connected"
        if connections:
            for conn in connections:
                other_device_id = conn[2] if conn[1] == self.device_instance.device_id else conn[1]
                other_device_type = self.get_device_info(other_device_id)
                connected_to = f"{other_device_type.capitalize()} (ID: {other_device_id})"

        self.add_port_row(0, 1, connected_to, mac, config_str)

    def populate_router_ports(self, connections):
        self.table.setRowCount(4)
        port_info = Database.cursor.execute(
            "SELECT port_number, mac_address, ip_address, subnet_mask, vlan FROM router_ports WHERE device_id = ?",
            (self.device_instance.device_id,)
        ).fetchall()
        port_dict = {row[0]: row[1:] for row in port_info}
        conn_dict = {}
        for conn in connections:
            if conn[1] == self.device_instance.device_id:
                conn_dict[conn[3]] = conn[2]
            else:
                conn_dict[conn[4]] = conn[1]
        for port_num in range(1, 5):
            connected_to = "Not connected"
            if port_num in conn_dict:
                other_device_id = conn_dict[port_num]
                other_device_type = self.get_device_info(other_device_id)
                connected_to = f"{other_device_type.capitalize()} (ID: {other_device_id})"
            if port_num in port_dict:
                mac, ip, subnet, vlan = port_dict[port_num]
                config_str = f"IP: {ip if ip else 'Not set'}\nSubnet: {subnet if subnet else 'Not set'}\nVLAN: {vlan if vlan else 'Not set'}"
            else:
                mac, config_str = "N/A", "Not configured"
            self.add_port_row(port_num - 1, port_num, connected_to, mac, config_str)

    def populate_switch_ports(self, connections):
        self.table.setRowCount(8)
        port_info = Database.cursor.execute(
            "SELECT port_number, mac_address, vlan, port_type FROM switch_ports WHERE device_id = ?",
            (self.device_instance.device_id,)
        ).fetchall()
        port_dict = {row[0]: row[1:] for row in port_info}
        conn_dict = {}
        for conn in connections:
            if conn[1] == self.device_instance.device_id:
                conn_dict[conn[3]] = conn[2]
            else:
                conn_dict[conn[4]] = conn[1]
        for port_num in range(1, 9):
            connected_to = "Not connected"
            if port_num in conn_dict:
                other_device_id = conn_dict[port_num]
                other_device_type = self.get_device_info(other_device_id)
                connected_to = f"{other_device_type.capitalize()} (ID: {other_device_id})"
            if port_num in port_dict:
                mac, vlan, port_type = port_dict[port_num]
                config_str = f"Type: {port_type if port_type else 'Not set'}\nVLAN: {vlan if vlan else 'Not set'}"
            else:
                mac, config_str = "N/A", "Not configured"
            self.add_port_row(port_num - 1, port_num, connected_to, mac, config_str)

    def add_port_row(self, row, port_num, connected_to, mac, config):
        self.table.setItem(row, 0, QTableWidgetItem(str(port_num)))
        self.table.setItem(row, 1, QTableWidgetItem(connected_to))
        self.table.setItem(row, 2, QTableWidgetItem(mac))
        self.table.setItem(row, 3, QTableWidgetItem(config))

class ConfigurationDialog(QDialog):
    def __init__(self, device_instance, parent=None):
        super().__init__(parent)
        self.device_instance = device_instance
        self.setWindowTitle(f"Configure {device_instance.device_type.capitalize()}")
        self.setup_ui()
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

    def setup_ui(self):
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        config_tab = QWidget()
        config_layout = QVBoxLayout()
        if self.device_instance.device_type == "computer":
            self.setup_computer_config(config_layout)
        elif self.device_instance.device_type == "router":
            self.setup_router_config(config_layout)
        elif self.device_instance.device_type == "switch":
            self.setup_switch_config(config_layout)
        config_tab.setLayout(config_layout)
        port_info_tab = PortInfoTab(self.device_instance)
        tab_widget.addTab(config_tab, "Configuration")
        tab_widget.addTab(port_info_tab, "Port Information")

        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def setup_computer_config(self, layout):
        grid = QGridLayout()
        grid.addWidget(QLabel("IP Address:"), 0, 0)
        self.ip_input = QLineEdit()
        grid.addWidget(self.ip_input, 0, 1)
        grid.addWidget(QLabel("Subnet Mask:"), 1, 0)
        self.subnet_input = QLineEdit()
        grid.addWidget(self.subnet_input, 1, 1)
        layout.addLayout(grid)
        apply_btn = QPushButton("Apply Configuration")
        apply_btn.clicked.connect(self.apply_computer_config)
        layout.addWidget(apply_btn)

    def setup_router_config(self, layout):
        grid = QGridLayout()
        grid.addWidget(QLabel("Port:"), 0, 0)
        self.port_select = QSpinBox()
        self.port_select.setMinimum(1)
        self.port_select.setMaximum(self.device_instance.number_of_ports)
        grid.addWidget(self.port_select, 0, 1)

        grid.addWidget(QLabel("IP Address:"), 1, 0)
        self.ip_input = QLineEdit()
        grid.addWidget(self.ip_input, 1, 1)

        grid.addWidget(QLabel("Subnet Mask:"), 2, 0)
        self.subnet_input = QLineEdit()
        grid.addWidget(self.subnet_input, 2, 1)

        grid.addWidget(QLabel("VLAN ID:"), 3, 0)
        self.vlan_input = QLineEdit()
        grid.addWidget(self.vlan_input, 3, 1)

        layout.addLayout(grid)
        apply_btn = QPushButton("Apply Configuration")
        apply_btn.clicked.connect(self.apply_router_config)
        layout.addWidget(apply_btn)

    def setup_switch_config(self, layout):
        grid = QGridLayout()
        grid.addWidget(QLabel("Port:"), 0, 0)
        self.port_select = QSpinBox()
        self.port_select.setMinimum(1)
        self.port_select.setMaximum(self.device_instance.number_of_ports)
        grid.addWidget(self.port_select, 0, 1)
        grid.addWidget(QLabel("Port Type:"), 1, 0)
        self.port_type = QComboBox()
        self.port_type.addItems(["access", "trunk"])
        grid.addWidget(self.port_type, 1, 1)
        grid.addWidget(QLabel("VLAN IDs (comma-separated):"), 2, 0)
        self.vlan_input = QLineEdit()
        grid.addWidget(self.vlan_input, 2, 1)
        layout.addLayout(grid)
        apply_btn = QPushButton("Apply Configuration")
        apply_btn.clicked.connect(self.apply_switch_config)
        layout.addWidget(apply_btn)

    def apply_computer_config(self):
        ip_address = self.ip_input.text()
        subnet_mask = self.subnet_input.text()

        if self.device_instance.set_interface_computer(ip_address, subnet_mask):
            QMessageBox.information(self, "Success", "Configuration applied successfully")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid IP address or subnet mask")

    def apply_router_config(self):
        port = self.port_select.value()
        ip_address = self.ip_input.text()
        subnet_mask = self.subnet_input.text()
        vlan_id = self.vlan_input.text()
        if  0 < int(vlan_id) <= 4096 and self.device_instance.set_interface_router(port, ip_address, subnet_mask, vlan_id):
            QMessageBox.information(self, "Success", "Configuration applied successfully")
            self.accept()
        else:

            QMessageBox.warning(self, "Error", "Invalid configuration parameters")

    def apply_switch_config(self):
        port = self.port_select.value()
        port_type = self.port_type.currentText()
        try:
            vlans = [int(v.strip()) for v in self.vlan_input.text().split(',') if v.strip()]
            if self.device_instance.set_interface_switch(port, vlans, port_type):
                QMessageBox.information(self, "Success", "Configuration applied successfully")
                self.accept()
            else:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid VLAN IDs")



