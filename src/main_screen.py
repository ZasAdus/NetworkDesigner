# Form implementation generated from reading ui file 'screen.ui'
#
# Created by: PyQt6 UI code generator 6.8.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QSizePolicy
import sys
from controller import Controller, Device
from database import Database




class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        Database.initialize(clear=True)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 70, 101, 300))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label_4 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignTop)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)

        self.router_icon = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.router_icon.setIcon(QIcon("icons/router.png"))
        self.router_icon.setIconSize(self.router_icon.size())
        self.router_icon.setObjectName("router_icon")
        self.router_icon.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 5;
                background: transparent;
                text-align: center;
            }
        """)
        self.router_icon.clicked.connect(lambda: Controller.picked_device("router"))
        self.verticalLayout.addWidget(self.router_icon)

        self.label = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignTop)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.switch_icon = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.switch_icon.setIcon(QIcon("icons/switch.png"))
        self.switch_icon.setIconSize(self.switch_icon.size())
        self.switch_icon.setObjectName("switch_icon")
        self.switch_icon.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 5;
                background: transparent;
                text-align: center;
            }
        """)
        self.switch_icon.clicked.connect(lambda: Controller.picked_device("switch"))
        self.verticalLayout.addWidget(self.switch_icon)

        self.label_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignTop)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)

        self.computer_icon = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.computer_icon.setIcon(QIcon("icons/computer.png"))
        self.computer_icon.setIconSize(self.computer_icon.size())
        self.computer_icon.setObjectName("computer_icon")
        self.computer_icon.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0;
                background: transparent;
                text-align: center;
            }
        """)
        self.computer_icon.clicked.connect(lambda: Controller.picked_device("computer"))
        self.verticalLayout.addWidget(self.computer_icon)
        self.label_3 = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignTop)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)

        self.connectButton = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.connectButton.setText("Connect Devices")
        self.connectButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.verticalLayout.addWidget(self.connectButton)
        self.connectButton.clicked.connect(Controller.connect_button)

        self.clearButton = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.clearButton.setText("Clear Design")
        self.clearButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.verticalLayout.addWidget(self.clearButton)
        self.clearButton.clicked.connect(Controller.clear_button)


        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(270, 10, 301, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.design_mode = QtWidgets.QRadioButton(parent=self.horizontalLayoutWidget)
        self.design_mode.setChecked(True)
        self.design_mode.setObjectName("design_mode")
        self.horizontalLayout.addWidget(self.design_mode)
        self.configure_mode = QtWidgets.QRadioButton(parent=self.horizontalLayoutWidget)
        self.configure_mode.setObjectName("configure_mode")
        self.horizontalLayout.addWidget(self.configure_mode)
        # self.test_mode = QtWidgets.QRadioButton(parent=self.horizontalLayoutWidget)
        # self.test_mode.setObjectName("test_mode")
        # self.horizontalLayout.addWidget(self.test_mode)
        # self.save_button = QtWidgets.QPushButton(parent=self.centralwidget)
        # self.save_button.setGeometry(QtCore.QRect(700, 540, 93, 28))
        # self.save_button.setObjectName("save_button")
        # self.save_button.clicked.connect(File.save_database_file)
        # self.load_button = QtWidgets.QPushButton(parent=self.centralwidget)
        # self.load_button.setGeometry(QtCore.QRect(600, 540, 93, 28))
        # self.load_button.setObjectName("load_button")
        # self.load_button.isEnabled()
        # #self.load_button.clicked.connect(File.load_database_file)
        self.bottom_canva = QtWidgets.QGraphicsView(parent=self.centralwidget)
        self.bottom_canva.setGeometry(QtCore.QRect(0, 530, 801, 51))
        self.bottom_canva.setStyleSheet("background-color: grey; border: 1px solid blue;")
        self.bottom_canva.setObjectName("bottom_canva")
        self.left_canva = QtWidgets.QGraphicsView(parent=self.centralwidget)
        self.left_canva.setGeometry(QtCore.QRect(0, -1, 101, 581))
        self.left_canva.setObjectName("left_canva")
        self.left_canva.setStyleSheet("background-color: grey; border: 1px solid blue;")
        self.top_canva = QtWidgets.QGraphicsView(parent=self.centralwidget)
        self.top_canva.setGeometry(QtCore.QRect(0, 0, 801, 51))
        self.top_canva.setObjectName("top_canva")
        self.top_canva.setStyleSheet("background-color: grey; border: 1px solid blue;")
        self.main_canva = QtWidgets.QGraphicsView(parent=self.centralwidget)
        self.main_canva.setGeometry(QtCore.QRect(89, 39, 711, 492))
        self.main_canva.setObjectName("main_canva")
        self.main_canva.setStyleSheet("background-color: white;")
        self.main_canva.raise_()
        Controller.initialize(self.main_canva, self)
        self.left_canva.raise_()
        self.top_canva.raise_()
        self.bottom_canva.raise_()
        self.verticalLayoutWidget.raise_()
        self.horizontalLayoutWidget.raise_()
        # self.save_button.raise_()
        # self.load_button.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NetworkDesigner"))
        self.label_4.setText(_translate("MainWindow", "Devices:"))
        self.label.setText(_translate("MainWindow", "Router"))
        self.label_2.setText(_translate("MainWindow", "Switch"))
        self.label_3.setText(_translate("MainWindow", "Computer"))
        self.design_mode.setText(_translate("MainWindow", "Design"))
        self.configure_mode.setText(_translate("MainWindow", "Configure"))
        # self.test_mode.setText(_translate("MainWindow", "Test"))
        # self.save_button.setText(_translate("MainWindow", "save"))
        # self.load_button.setText(_translate("MainWindow", "load"))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setFixedSize(800, 600)
    MainWindow.show()
    sys.exit(app.exec())
