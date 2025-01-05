from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget,
                             QVBoxLayout, QHBoxLayout, QGraphicsView,
                             QGraphicsScene, QFrame)
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QPen, QAction
from PyQt6.QtCore import Qt, QMimeData, QPoint
import sys
import os
from collections import deque

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class History:
    def __init__(self):
        self.undo_stack = deque(maxlen=20)  # Limit historii do 20 zmian
        self.redo_stack = deque(maxlen=20)

    def push(self, state):
        self.undo_stack.append(state)
        self.redo_stack.clear()  # Czyszczenie redo po nowej akcji

    def undo(self):
        if len(self.undo_stack) > 0:
            state = self.undo_stack.pop()
            self.redo_stack.append(state)
            return state
        return None

    def redo(self):
        if len(self.redo_stack) > 0:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            return state
        return None


class DeviceIcon(QLabel):
    def __init__(self, device_type, icon_path):
        super().__init__()
        self.device_type = device_type

        full_path = os.path.join(SCRIPT_DIR, icon_path)

        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                self.setPixmap(scaled_pixmap)
            else:
                self.setText(device_type)
        else:
            self.setText(device_type)

        self.setFixedSize(50, 50)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.device_type)
            drag.setMimeData(mime_data)
            drag.exec()


class DeviceNode(QLabel):
    def __init__(self, device_type, parent=None):
        super().__init__(parent)
        self.device_type = device_type
        self.original_pixmap = None

        full_path = os.path.join(SCRIPT_DIR, f"icons/{device_type}.png")

        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                self.original_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation)
                self.setPixmap(self.original_pixmap)
            else:
                self.setText(device_type)
        else:
            self.setText(device_type)

        self.setFixedSize(50, 50)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")
        self.connections = []

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            canvas = self.parent()
            if canvas:
                canvas.node_clicked(self)


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.nodes = []
        self.selected_node = None
        self.connections = []
        self.setStyleSheet("background-color: white;")
        self.history = History()

    def save_state(self):
        connections_state = [(n1, n2) for n1, n2 in self.connections]
        self.history.push(connections_state)

    def restore_state(self, state):
        if state is not None:
            self.connections = state
            self.update()
            if self.selected_node:
                self.selected_node.setStyleSheet("background-color: transparent;")
                self.selected_node = None

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        device_type = event.mimeData().text()
        node = DeviceNode(device_type, self)
        node.move(event.position().toPoint())
        node.show()
        self.nodes.append(node)
        self.save_state()

    def node_clicked(self, node):
        if self.selected_node is None:
            self.selected_node = node
            node.setStyleSheet("border: 1px solid lightblue; background-color: transparent;")
        else:
            if self.selected_node != node:
                connection = (self.selected_node, node)
                self.connections.append(connection)
                self.save_state()
                self.selected_node.setStyleSheet("background-color: transparent;")
            else:
                self.selected_node.setStyleSheet("background-color: transparent;")
            self.selected_node = None
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)

        for connection in self.connections:
            node1, node2 = connection
            start = node1.pos() + QPoint(25, 25)
            end = node2.pos() + QPoint(25, 25)
            painter.drawLine(start, end)

    def undo(self):
        self.restore_state(self.history.undo())

    def redo(self):
        self.restore_state(self.history.redo())


class NetworkDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Designer")
        self.setGeometry(100, 100, 800, 600)

        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)
        self.addAction(undo_action)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        self.addAction(redo_action)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.Shape.Box)
        sidebar.setMaximumWidth(100)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #3b3b3b;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)

        devices = {
            'router': 'icons/router.png',
            'switch': 'icons/switch.png',
            'computer': 'icons/computer.png'
        }

        for device_type, icon_path in devices.items():
            icon = DeviceIcon(device_type, icon_path)
            sidebar_layout.addWidget(icon)

        sidebar_layout.addStretch()

        self.canvas = Canvas()

        layout.addWidget(sidebar)
        layout.addWidget(self.canvas, stretch=1)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)

    def undo(self):
        self.canvas.undo()

    def redo(self):
        self.canvas.redo()


def main():
    app = QApplication(sys.argv)
    window = NetworkDesigner()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()