from PyQt6.QtWidgets import (QMessageBox, QPushButton, QGraphicsScene, QGraphicsLineItem,
                             QLabel)
from PyQt6.QtGui import QIcon, QPen
from PyQt6.QtCore import Qt
from router import Router
from computer import Computer
from configuration import ConfigurationDialog
from switch import Switch
from database import Database

devices = []

class Device:
    devices_to_connect = []

    def __init__(self, device_type, x, y, scene, device_id=None):
        try:
            self.device_type = device_type
            self.x = x
            self.y = y
            self.scene = scene
            if device_type == "router":
                self.device_instance = Router(x, y) if device_id is None else Router(x, y, device_id)
            elif device_type == "switch":
                self.device_instance = Switch(x, y) if device_id is None else Switch(x, y, device_id)
            elif device_type == "computer":
                self.device_instance = Computer(x, y) if device_id is None else Computer(x, y, device_id)
            else:
                raise ValueError(f"Invalid device type: {device_type}")

            if hasattr(self.device_instance, 'device_id'):
                self.button = QPushButton()
                self.button.resize(50, 50)
                self.button.setIcon(QIcon(f"icons/{device_type.lower()}.png"))
                self.button.setIconSize(self.button.size())
                self.button.setStyleSheet("""
                    QPushButton {
                        border: none;
                        padding: 0;
                        background: transparent;
                        text-align: center;
                    }
                """)
                self.button.mousePressEvent = self.device_clicked

                self.id_label = QLabel(f"ID: {self.device_instance.device_id}")
                self.id_label.setAlignment(Qt.AlignmentFlag.AlignBaseline)
                self.id_label.setStyleSheet("""
                    QLabel {
                        background: transparent;
                        color: black;
                        font-size: 10px;
                        font-weight: bold;
                    }
                """)

                self.id_proxy = scene.addWidget(self.id_label)
                self.id_proxy.setZValue(1)
                self.id_proxy.setPos(x, y + 50)

                self.button_proxy = scene.addWidget(self.button)
                self.button_proxy.setZValue(3)
                self.button_proxy.setPos(x, y)

                devices.append(self)
            else:
                raise ValueError("Device instance creation failed")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to create device: {str(e)}")
            if hasattr(self, 'button_proxy'):
                scene.removeItem(self.button_proxy)
            if hasattr(self, 'id_proxy'):
                scene.removeItem(self.id_proxy)
            raise

    def device_clicked(self, event):
        ui = Controller.ui_instance

        if ui.configure_mode.isChecked():
            dialog = ConfigurationDialog(self.device_instance)
            dialog.exec()
            return

        if ui.design_mode.isChecked() and Controller.connection_mode:
            available_port = Database.get_available_port(self.device_instance.device_id)
            if available_port is None:
                QMessageBox.warning(None, "Connection Error",
                                    f"No available ports on this {self.device_type}!")
                return

            if self not in Device.devices_to_connect:
                if len(Device.devices_to_connect) == 1:
                    other_device = Device.devices_to_connect[0]
                    connections = Database.get_device_connections(self.device_instance.device_id)
                    for conn in connections:
                        if (conn[1] == other_device.device_instance.device_id or
                                conn[2] == other_device.device_instance.device_id):
                            QMessageBox.warning(None, "Connection Error",
                                                "These devices are already connected!")
                            return

                Device.devices_to_connect.append(self)
                self.button.setStyleSheet("""
                    QPushButton {
                        border: none;
                        padding: 0;
                        background: lightblue;
                        text-align: center;
                    }
                """)

                if len(Device.devices_to_connect) == 2:
                    device1 = Device.devices_to_connect[0]
                    device2 = Device.devices_to_connect[1]
                    port1 = Database.get_available_port(device1.device_instance.device_id)
                    port2 = Database.get_available_port(device2.device_instance.device_id)

                    if port1 is not None and port2 is not None:
                        if Database.add_connection(
                                device1.device_instance.device_id,
                                device2.device_instance.device_id,
                                port1,
                                port2
                        ):
                            start_x = device1.x + 25
                            start_y = device1.y + 25
                            end_x = device2.x + 25
                            end_y = device2.y + 25
                            line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
                            pen = QPen(Qt.GlobalColor.black)
                            pen.setWidth(2)
                            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                            pen.setStyle(Qt.PenStyle.SolidLine)
                            line.setPen(pen)
                            line.setZValue(2)
                            Controller.scene.addItem(line)
                        else:
                            QMessageBox.warning(None, "Connection Error",
                                                "Failed to create connection in database!")

                    for device in Device.devices_to_connect:
                        device.button.setStyleSheet("""
                            QPushButton {
                                border: none;
                                padding: 0;
                                background: transparent;
                                text-align: center;
                            }
                        """)
                    Device.devices_to_connect.clear()

    @staticmethod
    def initialize():
        Device.devices_to_connect = []

class Controller:
    main_canva = None
    selected_device = None
    scene = None
    connection_mode = False
    ui_instance = None

    @staticmethod
    def initialize(main_canva, ui_instance):
        Controller.main_canva = main_canva
        Controller.scene = QGraphicsScene()
        Controller.main_canva.setScene(Controller.scene)
        Controller.ui_instance = ui_instance
        Device.initialize()

        ui_instance.design_mode.toggled.connect(Controller.on_mode_change)
        ui_instance.configure_mode.toggled.connect(Controller.on_mode_change)

    @staticmethod
    def on_mode_change(checked):
        ui = Controller.ui_instance

        Controller.connection_mode = False
        Controller.selected_device = None
        Device.devices_to_connect = []

        buttons_enabled = ui.design_mode.isChecked()
        ui.router_icon.setEnabled(buttons_enabled)
        ui.switch_icon.setEnabled(buttons_enabled)
        ui.computer_icon.setEnabled(buttons_enabled)
        ui.connectButton.setEnabled(buttons_enabled)
        ui.clearButton.setEnabled(buttons_enabled)


        for device in devices:
            device.button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 0;
                    background: transparent;
                    text-align: center;
                }
            """)

    @staticmethod
    def check_overlap(x, y):
        DEVICE_WIDTH = 50
        DEVICE_HEIGHT = 50

        for device in devices:
            device_left = device.x
            device_right = device.x + DEVICE_WIDTH
            device_top = device.y
            device_bottom = device.y + DEVICE_HEIGHT

            if (x < device_right and
                    x + DEVICE_WIDTH > device_left and
                    y < device_bottom and
                    y + DEVICE_HEIGHT > device_top):
                return True

        return False

    @staticmethod
    def on_canvas_click(event):
        if Controller.connection_mode or not Controller.selected_device:
            return
        pos = Controller.main_canva.mapToScene(event.pos())
        x = int(pos.x() - 25)
        y = int(pos.y() - 25)

        if Controller.check_overlap(x, y):
            QMessageBox.warning(None, "Placement Error",
                                "Cannot place device here - overlaps with existing device")
            return

        Device(Controller.selected_device, x, y, Controller.scene)

    @staticmethod
    def picked_device(device):
        if device is not None:
            Controller.selected_device = device
            Controller.connection_mode = False
            Controller.main_canva.mousePressEvent = Controller.on_canvas_click
            ui = Controller.ui_instance
            buttons = [ui.router_icon, ui.switch_icon, ui.computer_icon]
            selected_button = None

            if device == "router":
                selected_button = ui.router_icon
            elif device == "switch":
                selected_button = ui.switch_icon
            elif device == "computer":
                selected_button = ui.computer_icon

            if selected_button:
                Controller.highlight_device_button(selected_button, buttons)

    @staticmethod
    def connect_button():
        ui = Controller.ui_instance
        buttons = [ui.router_icon, ui.switch_icon, ui.computer_icon]
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 5;
                    background: transparent;
                    text-align: center;
                }
            """)
        Controller.connection_mode = True
        Controller.selected_device = None
        Device.devices_to_connect = []
        QMessageBox.information(None, "Connection Mode",
                                "Connection mode activated. Double-click two devices to connect them.")

    @staticmethod
    def highlight_device_button(device_button, buttons):
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 5;
                    background: transparent;
                    text-align: center;
                }
            """)
        device_button.setStyleSheet("""
            QPushButton {
                border: 1px solid blue;
                padding: 5;
                background: lightgray;
                text-align: center;
            }
        """)

    @staticmethod
    def clear_button():
        dialog = QMessageBox()
        dialog.setWindowTitle("Confirmation")
        dialog.setText("Are you sure you want to delete all devices?")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setIcon(QMessageBox.Icon.Warning)
        response = dialog.exec()
        if response == QMessageBox.StandardButton.Yes:
            Controller.scene.clear()
            devices.clear()
            Database.clear_all_tables()
            Device.devices_to_connect = []

    @staticmethod
    def get_devices():
        return Database.get_devices()

    @staticmethod
    def device_clicked(self, event):
        ui = Controller.ui_instance
        if ui.configure_mode.isChecked():
            dialog = ConfigurationDialog(self.device_instance)
            dialog.exec()
            return
        if not Controller.connection_mode:
            super().mousePressEvent(event)
            return