# main.py
import os
import sys
from pathlib import Path
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QVariant
from database import Database


class NetworkBackend(QObject):
    # Signal to notify QML about new device
    deviceCreated = pyqtSignal(str, int, float, float, arguments=['type', 'id', 'x', 'y'])

    def __init__(self):
        super().__init__()
        Database.initialize()
        self.devices = {}

    @pyqtSlot(str, float, float, result=bool)
    def create_device(self, device_type: str, x: float, y: float) -> bool:
        try:
            if device_type == "router":
                from router import Router
                device = Router(x=int(x), y=int(y))
            elif device_type == "switch":
                from switch import Switch
                device = Switch(x=int(x), y=int(y))
            elif device_type == "computer":
                from computer import Computer
                device = Computer(x=int(x), y=int(y))
            else:
                return False

            self.devices[device.device_id] = device
            # Emit signal with device info
            self.deviceCreated.emit(device_type, device.device_id, x, y)
            return True
        except Exception as e:
            print(f"Error creating device: {e}")
            return False

    @pyqtSlot(result=list)
    def get_devices(self):
        return Database.get_devices()


def main():
    app = QGuiApplication(sys.argv)

    # Create QML engine
    engine = QQmlApplicationEngine()

    # Create and expose backend to QML
    backend = NetworkBackend()
    engine.rootContext().setContextProperty("backend", backend)

    # Set up icon path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "qml")
    engine.addImportPath(icon_path)

    # Load QML file
    qml_file = os.path.join(current_dir, "qml/MainWindow.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()