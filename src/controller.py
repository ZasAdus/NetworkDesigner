from PyQt6.QtWidgets import (QInputDialog, QMessageBox, QGraphicsPixmapItem,
                             QPushButton, QGraphicsScene, QGraphicsLineItem, QWidget)
from PyQt6.QtGui import QPixmap, QIcon, QPen, QPainter
from PyQt6.QtCore import Qt, QPointF


devices = []
class Device(QPushButton):
    devices_to_connect = None

    def __init__(self, device_type, x, y, scene):
        super().__init__()
        self.device_type = device_type
        self.resize(50, 50)

        icon_path = f"icons/{device_type.lower()}.png"
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size())

        self.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0;
                background: transparent;
                text-align: center;
            }
        """)

        self.move(x, y)
        self.scene = scene
        self.x = x
        self.y = y
        proxy = scene.addWidget(self)
        proxy.setZValue(1)
        self.mousePressEvent = self.device_clicked
        devices.append(self)

    @staticmethod
    def initialize():
        Device.devices_to_connect = []

    def device_clicked(self, event):
        if not Controller.connection_mode:
            super().mousePressEvent(event)
            return

        if self not in Device.devices_to_connect:
            Device.devices_to_connect.append(self)
            self.setStyleSheet("""
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
                line.setZValue(0)
                Controller.scene.addItem(line)
                for device in Device.devices_to_connect:
                    device.setStyleSheet("""
                        QPushButton {
                            border: none;
                            padding: 0;
                            background: transparent;
                            text-align: center;
                        }
                    """)

                Device.devices_to_connect.clear()


class Controller:
    main_canva = None
    selected_device = None
    scene = None
    connection_mode = False

    @staticmethod
    def initialize(main_canva, ui_instance):
        Controller.main_canva = main_canva
        Controller.scene = QGraphicsScene()
        Controller.main_canva.setScene(Controller.scene)
        Controller.ui_instance = ui_instance
        Device.initialize()

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
    def on_canvas_click(event):
        if Controller.connection_mode or not Controller.selected_device:
            return

        pos = Controller.main_canva.mapToScene(event.pos())
        Device(
            Controller.selected_device,
            int(pos.x() - 25),
            int(pos.y() - 25),
            Controller.scene
        )

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
    def highlight_device_button(device_button, buttons):
        # Reset all buttons
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 5;
                    background: transparent;
                    text-align: center;
                }
            """)
        # Highlight the selected button
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
            for device in devices:
                device.scene.clear()

