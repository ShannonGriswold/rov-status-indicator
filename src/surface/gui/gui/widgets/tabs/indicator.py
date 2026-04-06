from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QPushButton

from gui.widgets.arm import Arm
from gui.widgets.heartbeat import HeartbeatWidget
from gui.widgets.ip_widget import IPWidget
from gui.widgets.logger import Logger
from rov_msgs.msg import vehicle_state
from rclpy.qos import qos_profile_system_default




class IndicatorTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.publisher = self.create_publisher(vehicle_state, "/hi", qos_profile_system_default)
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
        print(payload)
        self.publisher.publish(payload)
    

    def publish_disarm(self):
        payload = 'false'
        print(payload)
        self.publisher.publish(payload)
    