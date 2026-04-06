from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QPushButton

from gui.widgets.arm import Arm
from gui.widgets.heartbeat import HeartbeatWidget
from gui.widgets.ip_widget import IPWidget
from gui.widgets.logger import Logger




class IndicatorTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        top_bar = QHBoxLayout()
        button1 = QPushButton()
        button1.setText("ARM")
        button1.clicked.connect(self.publish_arm)
        top_bar.addWidget(button1)

        button2 = QPushButton()
        button2.setText("DISARM")
        button2.clicked.connect(self.publish_disarm)
        top_bar.addWidget(button2)


        top_bar.addStretch(2)
        root_layout = QVBoxLayout()
        root_layout.addLayout(top_bar)
        root_layout.addStretch()
        self.setLayout(root_layout)


    def publish_arm(self):
        payload = 'true'
        publish.single('/hi', payload, hostname='localhost')
        print(payload)
    

    def publish_disarm(self):
        payload = 'false'
        publish.single('/hi', payload, hostname='localhost')
        print(payload)
    