from PyQt6.QtWidgets import QListWidgetItem, QListWidget, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel
from rclpy.qos import qos_profile_system_default, qos_profile_default
from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot
from gui.gui_node import GUINode
from rov_msgs.msg import VehicleState
from rov_msgs.msg import StatusIPAddress

TOPIC_CHANGE_VEHICLE_STATE = '/indicator/changeVehicleState'
TOPIC_VEHICLE_STATE = '/indicator/vehicleState'
TOPIC_ADD_STATUS_INDICATOR = 'addStatusIndicator'

class IndicatorTab(QWidget):
    signal = pyqtSignal(VehicleState)
    def __init__(self) -> None:
        super().__init__()

        
        under_button_bar = QVBoxLayout()

        ip_input_row = QHBoxLayout()
        self.input = QLineEdit()
        ip_address_label = QLabel(text="IP Address: ")

        ip_input_row.addWidget(ip_address_label)
        ip_input_row.addWidget(self.input)

        ip_input_row.setStretchFactor(ip_address_label, 1)
        ip_input_row.setStretchFactor(self.input, 4)
        ip_input_row.addStretch(stretch=4)

        port_input_row = QHBoxLayout()
        self.port_input = QLineEdit()
        port_address_label = QLabel(text='Port: ')

        port_input_row.addWidget(port_address_label)
        port_input_row.addWidget(self.port_input)

        port_input_row.setStretchFactor(port_address_label, 1)
        port_input_row.setStretchFactor(self.port_input, 4)
        port_input_row.addStretch(stretch=4)

        add_ip_button_layout = QHBoxLayout()

        ip_button = QPushButton()
        ip_button.setText('Add IP address')
        ip_button.clicked.connect(self.add_ip)

        add_ip_button_layout.addWidget(ip_button)
        add_ip_button_layout.setStretchFactor(ip_button, 2)
        add_ip_button_layout.addStretch(7)



        under_button_bar.addLayout(ip_input_row)
        under_button_bar.addLayout(port_input_row)
        under_button_bar.addLayout(add_ip_button_layout)

        list_layout = QHBoxLayout()
        self.listWidget = QListWidget()
        list_layout.addWidget(self.listWidget)

        self.listWidget.setMaximumHeight(125)


        #print(self.input.maximumWidth())
        self.armed = False
        self.signal.connect(self.refresh)
        GUINode().create_signal_subscription(VehicleState, TOPIC_VEHICLE_STATE, self.signal)
        self.publisher = GUINode().create_publisher(VehicleState, TOPIC_CHANGE_VEHICLE_STATE,
                                                    qos_profile_system_default)
        self.IPPublisher = GUINode().create_publisher(StatusIPAddress, TOPIC_ADD_STATUS_INDICATOR,
                                                      qos_profile_system_default)


        top_bar = QHBoxLayout()

        button1 = QPushButton()
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
        root_layout.addLayout(list_layout)
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

    def add_ip(self) -> None:
        ip_input = self.input.text()
        try:
            port_number = int(self.port_input.text())
            payload = StatusIPAddress(ip_address = ip_input, port = port_number)
            self.IPPublisher.publish(payload)
            ip_item = QListWidgetItem(f'IP Address: {ip_input} \tPort: {port_number}')
            self.listWidget.addItem(ip_item)
        except (TypeError, ValueError):
            GUINode().get_logger().error("Invalid port")
        
        
        
    
    @pyqtSlot(VehicleState)
    def refresh(self, msg: VehicleState) -> None:
        if msg.armed:
            self.armed = True
            self.armed_label.setText("Armed")
        else:
            self.armed = False
            self.armed_label.setText("Disarmed")
        


           
