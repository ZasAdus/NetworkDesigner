import sqlite3
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen
import controller
import shutil

class Database:
    connection = None
    cursor = None

    @staticmethod
    def initialize(clear=False):
        if Database.connection is None:
            Database.connection = sqlite3.connect('network.db')
            Database.cursor = Database.connection.cursor()

            Database.cursor.executescript('''
                CREATE TABLE IF NOT EXISTS devices (
                    device_id INTEGER PRIMARY KEY,
                    mac_address TEXT NOT NULL,
                    device_type TEXT,
                    x INTEGER,
                    y INTEGER
                );

                CREATE TABLE IF NOT EXISTS router_ports (
                    device_id INTEGER,
                    port_number INTEGER,
                    mac_address TEXT UNIQUE,
                    ip_address TEXT,
                    subnet_mask TEXT,
                    vlan INTEGER,
                    PRIMARY KEY (device_id, port_number),
                    FOREIGN KEY (device_id) REFERENCES devices(device_id)
                );

                CREATE TABLE IF NOT EXISTS switch_ports (
                    device_id INTEGER,
                    port_number INTEGER,
                    mac_address TEXT UNIQUE,
                    vlan TEXT,
                    port_type TEXT CHECK(port_type IN ('access', 'trunk')),
                    PRIMARY KEY (device_id, port_number),
                    FOREIGN KEY (device_id) REFERENCES devices(device_id)
                );

                CREATE TABLE IF NOT EXISTS computer_ports (
                    device_id INTEGER PRIMARY KEY,
                    mac_address TEXT UNIQUE,
                    ip_address TEXT,
                    subnet_mask TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices(device_id)
                );

                CREATE TABLE IF NOT EXISTS connections (
                    connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device1_id INTEGER,
                    device2_id INTEGER,
                    device1_port INTEGER,
                    device2_port INTEGER,
                    FOREIGN KEY (device1_id) REFERENCES devices(device_id),
                    FOREIGN KEY (device2_id) REFERENCES devices(device_id),
                    UNIQUE(device1_id, device1_port),
                    UNIQUE(device2_id, device2_port)
                );
            ''')
            Database.connection.commit()
        if clear:
            Database.clear_all_tables()

    @staticmethod
    def add_connection(device1_id, device2_id, device1_port, device2_port):
        try:
            Database.cursor.execute('''
                    INSERT INTO connections 
                    (device1_id, device2_id, device1_port, device2_port)
                    VALUES (?, ?, ?, ?)
                ''', (device1_id, device2_id, device1_port, device2_port))
            Database.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def remove_connection(device1_id, device2_id):
        Database.cursor.execute('''
                DELETE FROM connections 
                WHERE (device1_id = ? AND device2_id = ?)
                OR (device1_id = ? AND device2_id = ?)
            ''', (device1_id, device2_id, device2_id, device1_id))
        Database.connection.commit()

    @staticmethod
    def get_device_connections(device_id):
        Database.cursor.execute('''
                SELECT * FROM connections 
                WHERE device1_id = ? OR device2_id = ?
            ''', (device_id, device_id))
        return Database.cursor.fetchall()

    @staticmethod
    def get_available_port(device_id):
        device_type = Database.get_device_type(device_id)
        max_ports = {"router": 4, "switch": 8, "computer": 1}
        Database.cursor.execute('''
                SELECT device1_port FROM connections WHERE device1_id = ?
                UNION
                SELECT device2_port FROM connections WHERE device2_id = ?
            ''', (device_id, device_id))

        used_ports = {port[0] for port in Database.cursor.fetchall()}
        for port in range(1, max_ports.get(device_type, 1) + 1):
            if port not in used_ports:
                return port
        return None

    @staticmethod
    def get_device_type(device_id):
        Database.cursor.execute('''
                SELECT device_type FROM devices WHERE device_id = ?
            ''', (device_id,))
        result = Database.cursor.fetchone()
        return result[0] if result else None

    @staticmethod
    def get_next_device_id():
        Database.cursor.execute("SELECT MAX(device_id) FROM devices")
        result = Database.cursor.fetchone()[0]
        return 1 if result is None else result + 1

    @staticmethod
    def mac_exists(mac_address):
        Database.cursor.execute('''
            SELECT EXISTS (
                SELECT 1 FROM (
                    SELECT mac_address FROM devices
                    UNION ALL
                    SELECT mac_address FROM router_ports
                    UNION ALL
                    SELECT mac_address FROM switch_ports
                    UNION ALL
                    SELECT mac_address FROM computer_ports
                ) WHERE mac_address = ?
            )
        ''', (mac_address,))
        return bool(Database.cursor.fetchone()[0])
    
    @staticmethod
    def insert_device(device_id, mac_address, device_type, x, y):
        Database.cursor.execute(
            "INSERT INTO devices (device_id, mac_address, device_type, x, y) VALUES (?, ?, ?, ?, ?)",
            (device_id, mac_address, device_type, x, y)
        )
        Database.connection.commit()
    
    @staticmethod
    def insert_port_router(device_id, port_number, mac_address, ip_address=None, subnet_mask=None, vlan=None):
        Database.cursor.execute('''
            INSERT INTO router_ports (device_id, port_number, mac_address, ip_address, subnet_mask, vlan)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device_id, port_number, mac_address, ip_address, subnet_mask, vlan))
        Database.connection.commit()

    @staticmethod
    def insert_port_switch(device_id, port_number, mac_address, vlan=None, port_type=None):
        Database.cursor.execute('''
            INSERT INTO switch_ports (device_id, port_number, mac_address, vlan, port_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (device_id, port_number, mac_address, vlan, port_type))
        Database.connection.commit()

    # @staticmethod
    # def insert_port_computer(device_id, mac_address, ip_address=None, subnet_mask=None):
    #     Database.cursor.execute('''
    #         INSERT INTO computer_ports (device_id, mac_address, ip_address, subnet_mask)
    #         VALUES (?, ?, ?, ?)
    #     ''', (device_id, mac_address, ip_address, subnet_mask))
    #     Database.connection.commit()

    @staticmethod
    def update_port_router(device_id, port_number, ip_address=None, subnet_mask=None, vlan=None):
        Database.cursor.execute('''
            UPDATE router_ports 
            SET ip_address = ?,
                subnet_mask = ?,
                vlan = ?
            WHERE device_id = ? AND port_number = ?
        ''', (ip_address, subnet_mask, vlan, device_id, port_number))
        Database.connection.commit()

    @staticmethod
    def update_port_switch(device_id, port_number, vlan, port_type):
        Database.cursor.execute('''
            UPDATE switch_ports 
            SET vlan = ?,
                port_type = ?
            WHERE device_id = ? AND port_number = ?
        ''', (vlan, port_type, device_id, port_number))
        Database.connection.commit()

    # @staticmethod
    # def update_port_computer(device_id, ip_address=None, subnet_mask=None):
    #     Database.cursor.execute('''
    #         UPDATE computer_ports
    #         SET ip_address = ?,
    #             subnet_mask = ?
    #         WHERE device_id = ?
    #     ''', (ip_address, subnet_mask, device_id))
    #     Database.connection.commit()

    @staticmethod
    def clear_all_tables():
        Database.cursor.execute('DELETE FROM devices')
        Database.cursor.execute('DELETE FROM router_ports')
        Database.cursor.execute('DELETE FROM switch_ports')
        Database.cursor.execute('DELETE FROM computer_ports')
        Database.cursor.execute('DELETE FROM connections')
        Database.connection.commit()

    
    @staticmethod
    def get_devices():
        Database.cursor.execute("SELECT * FROM devices")
        return Database.cursor.fetchall()


class File:

    # def load_database_file(self):
    #     try:
    #         file_dialog = QFileDialog()
    #         file_dialog.setNameFilter("Database files (*.db)")
    #         file_dialog.setDefaultSuffix("db")
    #
    #         if file_dialog.exec():
    #             selected_files = file_dialog.selectedFiles()
    #             if selected_files:
    #                 source_db_path = selected_files[0]
    #                 if Database.connection:
    #                     Database.connection.close()
    #                     Database.connection = None
    #                 if os.path.exists("network.db"):
    #                     os.remove("network.db")
    #                 shutil.copy(source_db_path, "network.db")
    #                 Database.initialize()
    #                 Database.cursor.execute("SELECT COUNT(*) FROM devices")
    #                 device_count = Database.cursor.fetchone()[0]
    #                 if device_count == 0:
    #                     QMessageBox.warning(
    #                         None,
    #                         "Error",
    #                         "No devices found in the selected database file."
    #                     )
    #                     return False
    #
    #                 controller.Controller.scene.clear()
    #                 controller.devices.clear()
    #                 controller.Device.devices_to_connect.clear()
    #
    #                 devices = Database.get_devices()
    #                 device_map = {}
    #
    #                 for device in devices:
    #                     device_id, mac_address, device_type, x, y = device
    #                     try:
    #                         new_device = controller.Device(device_type, x, y, controller.Controller.scene)
    #                         device_map[device_id] = new_device
    #                     except Exception as e:
    #                         print(f"Error creating device {device_id}: {e}")
    #
    #                 connections = Database.cursor.execute("SELECT * FROM connections").fetchall()
    #                 for connection in connections:
    #                     conn_id, device1_id, device2_id, device1_port, device2_port = connection
    #                     if device1_id in device_map and device2_id in device_map:
    #                         device1 = device_map[device1_id]
    #                         device2 = device_map[device2_id]
    #
    #                         start_x = device1.x + 25
    #                         start_y = device1.y + 25
    #                         end_x = device2.x + 25
    #                         end_y = device2.y + 25
    #                         line = controller.Controller.scene.addLine(start_x, start_y, end_x, end_y)
    #                         pen = QPen(Qt.GlobalColor.black)
    #                         pen.setWidth(2)
    #                         pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    #                         pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    #                         pen.setStyle(Qt.PenStyle.SolidLine)
    #                         line.setPen(pen)
    #                         line.setZValue(2)
    #
    #                 controller.Controller.main_canva.viewport().update()
    #                 QMessageBox.information(
    #                     None,
    #                     "Success",
    #                     f"Successfully loaded {len(devices)} devices and {len(connections)} connections."
    #                 )
    #                 return True
    #     except Exception as e:
    #         QMessageBox.critical(
    #             None,
    #             "Error",
    #             f"Failed to load network configuration: {str(e)}"
    #         )
    #         Database.initialize(clear=True)
    #         return False

    def save_database_file(self):
        try:
            if not Database.connection:
                QMessageBox.warning(None, "Error", "No active database connection.")
                return False

            file_dialog = QFileDialog()
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilter("Database files (*.db)")
            file_dialog.setDefaultSuffix("db")
            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    destination_path = selected_files[0]
                    Database.connection.commit()
                    Database.connection.close()
                    Database.connection = None
                    try:
                        import shutil
                        shutil.copy2('network.db', destination_path)
                        QMessageBox.information(
                            None,
                            "Success",
                            "Network configuration saved successfully!"
                        )
                        return True
                    except Exception as e:
                        QMessageBox.critical(
                            None,
                            "Error",
                            f"Failed to save database file: {str(e)}"
                        )
                        return False

                    finally:
                        Database.initialize()

        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Error during save operation: {str(e)}"
            )
            return False