from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from rclpy.qos import qos_profile_system_default

from gui.gui_node import GUINode
from rov_msgs.msg import VehicleState

TOPIC_CHANGE_VEHICLE_STATE = '/indicator/changeVehicleState'

class IndicatorTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.publisher = GUINode().create_publisher(VehicleState, TOPIC_CHANGE_VEHICLE_STATE,
                                                    qos_profile_system_default)
        top_bar = QHBoxLayout()
        button1 = QPushButton()
        button1.setText('ARM')
        button1.clicked.connect(self.publish_arm)
        top_bar.addWidget(button1)

        button2 = QPushButton()
        button2.setText('DISARM')
        button2.clicked.connect(self.publish_disarm)
        top_bar.addWidget(button2)


        top_bar.addStretch(2)
        root_layout = QVBoxLayout()
        root_layout.addLayout(top_bar)
        root_layout.addStretch()
        self.setLayout(root_layout)


    def publish_arm(self) -> None:
        payload = VehicleState(pi_connected = True, ardusub_connected = True, armed = True)
        print(payload)
        self.publisher.publish(payload)


    def publish_disarm(self) -> None:
        payload = VehicleState(pi_connected = True, ardusub_connected = True, armed = False)
        print(payload)
        self.publisher.publish(payload)
