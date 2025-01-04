import sqlite3

class Database:
    @staticmethod
    def initialize():
        Database.connection = sqlite3.connect('network.db')
        Database.cursor = Database.connection.cursor()
        Database.cursor.executescript('''
            DROP TABLE IF EXISTS devices;
            DROP TABLE IF EXISTS router_ports;
            DROP TABLE IF EXISTS switch_ports;
            DROP TABLE IF EXISTS computer_ports;
        ''')
        Database.cursor.executescript('''
            CREATE TABLE devices (
                device_id INTEGER PRIMARY KEY,
                mac_address TEXT NOT NULL,
                ip_address TEXT,
                device_type TEXT,
                x INTEGER,
                y INTEGER
            );

            CREATE TABLE router_ports (
                device_id INTEGER,
                port_number INTEGER,
                mac_address TEXT UNIQUE,
                ip_address TEXT,
                subnet_mask TEXT,
                vlan INTEGER,
                PRIMARY KEY (device_id, port_number),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            );

            CREATE TABLE switch_ports (
                device_id INTEGER,
                port_number INTEGER,
                mac_address TEXT UNIQUE,
                vlan TEXT,
                port_type TEXT CHECK(port_type IN ('access', 'trunk')),
                PRIMARY KEY (device_id, port_number),
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            );

            CREATE TABLE computer_ports (
                device_id INTEGER PRIMARY KEY,
                mac_address TEXT UNIQUE,
                ip_address TEXT,
                subnet_mask TEXT,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            );
        ''')

        Database.connection.commit()

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
    def insert_device(device_id, mac_address, ip_address, device_type, x, y):
        Database.cursor.execute(
            "INSERT INTO devices (device_id, mac_address, ip_address, device_type, x, y) VALUES (?, ?, ?, ?, ?, ?)",
            (device_id, mac_address, ip_address, device_type, x, y)
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

    @staticmethod
    def insert_port_computer(device_id, mac_address, ip_address=None, subnet_mask=None):
        Database.cursor.execute('''
            INSERT INTO computer_ports (device_id, mac_address, ip_address, subnet_mask)
            VALUES (?, ?, ?, ?)
        ''', (device_id, mac_address, ip_address, subnet_mask))
        Database.connection.commit()

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

    @staticmethod
    def update_port_computer(device_id, ip_address=None, subnet_mask=None):
        Database.cursor.execute('''
            UPDATE computer_ports
            SET ip_address = ?,
                subnet_mask = ?
            WHERE device_id = ?
        ''', (ip_address, subnet_mask, device_id))
        Database.connection.commit()

    @staticmethod
    def clear_table():
        Database.cursor.execute('DELETE FROM devices')
        Database.connection.commit()
    
    @staticmethod
    def clear_ports_tables():
        Database.cursor.execute('DELETE FROM router_ports')
        Database.cursor.execute('DELETE FROM switch_ports')
        Database.cursor.execute('DELETE FROM computer_ports')
        Database.connection.commit()
    
    @staticmethod
    def get_devices():
        Database.cursor.execute("SELECT * FROM devices")
        return Database.cursor.fetchall()