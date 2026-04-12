from PyQt6.QtWidgets import  QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel
from rclpy.qos import qos_profile_system_default
from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot

from gui.gui_node import GUINode, qos_profile_default
from rov_msgs.msg import VehicleState

TOPIC_CHANGE_VEHICLE_STATE = '/indicator/changeVehicleState'
TOPIC_VEHICLE_STATE = '/indicator/vehicleState'

class IndicatorTab(QWidget):
    signal = pyqtSignal(VehicleState)
    def __init__(self) -> None:
        super().__init__()
        self.input = QLineEdit(self)
        #print(self.input.maximumWidth())
        self.armed = False
        self.signal.connect(self.refresh)
        GUINode().create_signal_subscription(VehicleState, TOPIC_VEHICLE_STATE, self.signal, qos_profile_default)
        self.publisher = GUINode().create_publisher(VehicleState, TOPIC_CHANGE_VEHICLE_STATE,
                                                    qos_profile_system_default)
    

        top_bar = QHBoxLayout()
        under_button_bar = QHBoxLayout()
        button1 = QPushButton()
        under_button_bar.addWidget(self.input)
        self.armed_label = QLabel('Disarmed')
        top_bar.addWidget(self.armed_label)
        button1.setText('ARM')
        button1.clicked.connect(self.publish_arm)
        top_bar.addWidget(button1)


    
        button2 = QPushButton()
        button2.setText('DISARM')
        button2.clicked.connect(self.publish_disarm)
        top_bar.addWidget(button2)


        top_bar.addStretch(2)
        root_layout = QVBoxLayout()
        root_layout.addLayout(under_button_bar)
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
        
    
    @pyqtSlot(VehicleState)
    def refresh(self, msg: VehicleState) -> None:
        if msg.armed:
            self.armed = True
            self.armed_label.setText("Armed")
        else:
            self.armed = False
            self.armed_label.setText("Disarmed")
        


           
