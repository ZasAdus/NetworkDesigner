from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout,
                            QPushButton, QComboBox, QMessageBox,
                            QWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView)
from database import Database
from network_validator import NetworkValidator


class PortInfoTab(QWidget):
    def __init__(self, device_instance):
        super().__init__()
        self.device_instance = device_instance
        self.port_type_combos = {}
        self.validator = NetworkValidator()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()

        if self.device_instance.device_type == "router":
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(
                ["Port", "Connected To", "MAC Address", "IP Address", "Subnet Mask", "VLAN"]
            )
        elif self.device_instance.device_type == "switch":
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(
                ["Port", "Connected To", "MAC Address", "VLAN", "Port Type"]
            )
        elif self.device_instance.device_type == "computer":
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(
                ["Port", "Connected To", "MAC Address", "IP Address", "Subnet Mask"]
            )

        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        self.populate_port_info()
        layout.addWidget(self.table)

        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_configuration)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def add_port_row(self, row, port_num, connected_to, mac, ip, subnet, vlan=None, port_type=None):
        try:
            # Create items for first 3 columns and make them non-editable
            port_item = QTableWidgetItem(str(port_num))
            port_item.setFlags(port_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, port_item)

            connected_to_item = QTableWidgetItem(connected_to)
            connected_to_item.setFlags(connected_to_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, connected_to_item)

            mac_item = QTableWidgetItem(mac)
            mac_item.setFlags(mac_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, mac_item)

            if self.device_instance.device_type in ["router", "computer"]:
                ip_item = QTableWidgetItem(ip)
                subnet_item = QTableWidgetItem(subnet)

                ip_item.setFlags(ip_item.flags() | Qt.ItemFlag.ItemIsEditable)
                subnet_item.setFlags(subnet_item.flags() | Qt.ItemFlag.ItemIsEditable)

                self.table.setItem(row, 3, ip_item)
                self.table.setItem(row, 4, subnet_item)

                if self.device_instance.device_type == "router":
                    vlan_item = QTableWidgetItem(vlan)
                    vlan_item.setFlags(vlan_item.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row, 5, vlan_item)

            elif self.device_instance.device_type == "switch":
                vlan_item = QTableWidgetItem(vlan)
                vlan_item.setFlags(vlan_item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 3, vlan_item)

                combo = QComboBox()
                combo.addItems(['access', 'trunk'])
                if port_type in ['access', 'trunk']:
                    combo.setCurrentText(port_type)
                else:
                    combo.setCurrentText('trunk')

                self.port_type_combos[row] = combo
                self.table.setCellWidget(row, 4, combo)

        except Exception as e:
            print(f"Error adding row: {e}")

    def populate_port_info(self):
        device_id = self.device_instance.device_id
        device_type = self.device_instance.device_type
        connections = Database.get_device_connections(device_id)

        if device_type == "computer":
            self.table.setRowCount(1)
            port_info = Database.cursor.execute(
                "SELECT mac_address, ip_address, subnet_mask FROM computer_ports WHERE device_id = ?",
                (device_id,)
            ).fetchone()

            if port_info:
                mac = port_info[0] if port_info[0] else "N/A"
                ip = port_info[1] if port_info[1] else "Not set"
                subnet = port_info[2] if port_info[2] else "Not set"
            else:
                mac, ip, subnet = "N/A", "Not set", "Not set"

            connected_to = "Not connected"
            for conn in connections:
                if conn[1] == device_id:
                    other_id = conn[2]
                else:
                    other_id = conn[1]
                other_type = self.get_device_info(other_id)
                if other_type:
                    connected_to = f"{other_type.capitalize()} (ID: {other_id})"

            self.add_port_row(0, 1, connected_to, mac, ip, subnet)

        elif device_type == "router":
            self.table.setRowCount(4)
            port_info = Database.cursor.execute(
                "SELECT port_number, mac_address, ip_address, subnet_mask, vlan FROM router_ports WHERE device_id = ?",
                (device_id,)
            ).fetchall()

            port_dict = {row[0]: row[1:] for row in port_info}
            for port_num in range(1, 5):
                connected_to = "Not connected"
                for conn in connections:
                    if (conn[1] == device_id and conn[3] == port_num) or (conn[2] == device_id and conn[4] == port_num):
                        other_id = conn[2] if conn[1] == device_id else conn[1]
                        other_type = self.get_device_info(other_id)
                        if other_type:
                            connected_to = f"{other_type.capitalize()} (ID: {other_id})"

                if port_num in port_dict:
                    mac, ip, subnet, vlan = port_dict[port_num]
                else:
                    mac = f"00:00:00:00:{device_id:02x}:{port_num:02x}"
                    ip, subnet, vlan = "Not set", "Not set", "Not set"

                self.add_port_row(port_num - 1, port_num, connected_to, mac, ip, subnet, vlan)

        elif device_type == "switch":
            self.table.setRowCount(8)
            port_info = Database.cursor.execute(
                "SELECT port_number, mac_address, vlan, port_type FROM switch_ports WHERE device_id = ?",
                (device_id,)
            ).fetchall()

            port_dict = {row[0]: row[1:] for row in port_info}
            for port_num in range(1, 9):
                connected_to = "Not connected"
                for conn in connections:
                    if (conn[1] == device_id and conn[3] == port_num) or (conn[2] == device_id and conn[4] == port_num):
                        other_id = conn[2] if conn[1] == device_id else conn[1]
                        other_type = self.get_device_info(other_id)
                        if other_type:
                            connected_to = f"{other_type.capitalize()} (ID: {other_id})"

                if port_num in port_dict:
                    mac, vlan, port_type = port_dict[port_num]
                else:
                    mac = f"00:00:00:00:{device_id:02x}:{port_num:02x}"
                    vlan, port_type = "Not set", "trunk"

                self.add_port_row(port_num - 1, port_num, connected_to, mac, "N/A", "N/A", vlan, port_type)

    def get_device_info(self, device_id):
        return Database.cursor.execute(
            "SELECT device_type FROM devices WHERE device_id = ?",
            (device_id,)
        ).fetchone()[0]

    def save_configuration(self):
        try:
            device_id = self.device_instance.device_id

            if self.device_instance.device_type == "switch":
                for row in range(self.table.rowCount()):
                    port_number = int(self.table.item(row, 0).text())
                    vlan = self.table.item(row, 3).text() if self.table.item(row, 3) else "Not set"

                    combo = self.port_type_combos.get(row)
                    port_type = combo.currentText() if combo else 'trunk'

                    exists = Database.cursor.execute(
                        "SELECT 1 FROM switch_ports WHERE device_id = ? AND port_number = ?",
                        (device_id, port_number)
                    ).fetchone()

                    if exists:
                        Database.update_port_switch(device_id, port_number, vlan, port_type)
                    else:
                        mac_address = f"00:00:00:00:{device_id:02x}:{port_number:02x}"
                        Database.insert_port_switch(device_id, port_number, mac_address, vlan, port_type)

            elif self.device_instance.device_type == "computer":
                ip_address = self.table.item(0, 3).text() if self.table.item(0, 3) else "Not set"
                subnet_mask = self.table.item(0, 4).text() if self.table.item(0, 4) else "Not set"

                exists = Database.cursor.execute(
                    "SELECT 1 FROM computer_ports WHERE device_id = ?",
                    (device_id,)
                ).fetchone()

                if exists:
                    Database.update_port_computer(device_id, ip_address, subnet_mask)
                else:
                    mac_address = f"00:00:00:00:00:{device_id:02x}"
                    Database.insert_port_computer(device_id, mac_address, ip_address, subnet_mask)

            elif self.device_instance.device_type == "router":
                for row in range(self.table.rowCount()):
                    port_number = int(self.table.item(row, 0).text())
                    ip_address = self.table.item(row, 3).text() if self.table.item(row, 3) else "Not set"
                    subnet_mask = self.table.item(row, 4).text() if self.table.item(row, 4) else "Not set"
                    vlan = self.table.item(row, 5).text() if self.table.item(row, 5) else "Not set"
                    Database.update_port_router(device_id, port_number, ip_address, subnet_mask, vlan)

            QMessageBox.information(self, "Success", "Configuration saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

class ConfigurationDialog(QDialog):
    def __init__(self, device_instance, parent=None):
        super().__init__(parent)
        self.device_instance = device_instance
        self.setWindowTitle(f"Konfiguracja {device_instance.device_type.capitalize()}")
        self.setup_ui()
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

    def setup_ui(self):
        layout = QVBoxLayout()
        port_info_tab = PortInfoTab(self.device_instance)
        layout.addWidget(port_info_tab)
        self.setLayout(layout)