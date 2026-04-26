from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from rclpy.qos import qos_profile_system_default

from gui.gui_node import GUINode
from gui.styles.custom_styles import WidgetState
from gui.widgets.circle import CircleIndicator
from rov_msgs.msg import StatusIPAddress, VehicleState

TOPIC_CHANGE_VEHICLE_STATE = '/indicator/changeVehicleState'
TOPIC_VEHICLE_STATE = '/indicator/vehicleState'
TOPIC_ADD_STATUS_INDICATOR = 'addStatusIndicator'

class IndicatorTab(QWidget):
    signal = pyqtSignal(VehicleState)
    def __init__(self) -> None:
        super().__init__()

        self.armed = False
        self.pi = False
        self.ardusub = False
        self.signal.connect(self.refresh)
        GUINode().create_signal_subscription(VehicleState, TOPIC_VEHICLE_STATE, self.signal)
        self.publisher = GUINode().create_publisher(VehicleState, TOPIC_CHANGE_VEHICLE_STATE,
                                                    qos_profile_system_default)
        self.IPPublisher = GUINode().create_publisher(StatusIPAddress, TOPIC_ADD_STATUS_INDICATOR,
                                                      qos_profile_system_default)

        root_layout = QVBoxLayout()
        root_layout.addWidget(self.create_indicator_group())
        root_layout.addWidget(self.create_simulation_group())
        root_layout.addStretch()
        self.setLayout(root_layout)


    def create_indicator_group(self) -> QGroupBox:
        indicator_group = QGroupBox('Status Indicators')

        add_indicator_section = QVBoxLayout()

        ip_input_row = QHBoxLayout()
        self.input = QLineEdit()
        ip_address_label = QLabel(text='IP Address: ')

        ip_input_row.addWidget(ip_address_label)
        ip_input_row.addWidget(self.input)

        ip_input_row.setStretchFactor(ip_address_label, 1)
        ip_input_row.setStretchFactor(self.input, 3)
        ip_input_row.addStretch(stretch=4)

        port_input_row = QHBoxLayout()
        self.port_input = QLineEdit()
        port_address_label = QLabel(text='Port: ')

        port_input_row.addWidget(port_address_label)
        port_input_row.addWidget(self.port_input)

        port_input_row.setStretchFactor(port_address_label, 1)
        port_input_row.setStretchFactor(self.port_input, 3)
        port_input_row.addStretch(stretch=4)

        add_ip_button_layout = QHBoxLayout()

        ip_button = QPushButton()
        ip_button.setText('Add IP address')
        ip_button.clicked.connect(self.add_ip)

        add_ip_button_layout.addWidget(ip_button)
        add_ip_button_layout.setStretchFactor(ip_button, 2)
        add_ip_button_layout.addStretch(8)

        self.listWidget = QListWidget()
        self.listWidget.setMaximumHeight(125)

        add_indicator_section.addLayout(ip_input_row)
        add_indicator_section.addLayout(port_input_row)
        add_indicator_section.addLayout(add_ip_button_layout)
        add_indicator_section.addWidget(self.listWidget)

        indicator_group.setLayout(add_indicator_section)

        return indicator_group

    def create_simulation_group(self) -> QGroupBox:
        simulation_group = QGroupBox('Simulation Controls')

        simulation_layout = QGridLayout()

        self.armed_label = QLabel('Disarmed')
        self.arm_indicator = CircleIndicator(radius=10)
        self.arm_indicator.set_state(WidgetState.OFF)

        arm_button = QPushButton()
        arm_button.setText('ARM')
        arm_button.clicked.connect(self.publish_arm)

        disarm_button = QPushButton()
        disarm_button.setText('DISARM')
        disarm_button.clicked.connect(self.publish_disarm)

        simulation_layout.addWidget(self.armed_label, 0, 1)
        simulation_layout.addWidget(self.arm_indicator, 0, 2)
        simulation_layout.addWidget(arm_button, 0, 3)
        simulation_layout.addWidget(disarm_button, 0, 4)
        
        self.pi_label = QLabel('Pi Disconnected')
        self.pi_indicator = CircleIndicator(radius=10)
        self.pi_indicator.set_state(WidgetState.OFF)

        pi_connected_button = QPushButton()
        pi_connected_button.setText('Pi connected')
        pi_connected_button.clicked.connect(self.publish_pi_connected)

        pi_disconnected_button = QPushButton()
        pi_disconnected_button.setText('Pi disconnected')
        pi_disconnected_button.clicked.connect(self.publish_pi_disconnected)

        simulation_layout.addWidget(self.pi_label, 1, 1)
        simulation_layout.addWidget(self.pi_indicator, 1, 2)
        simulation_layout.addWidget(pi_connected_button, 1, 3)
        simulation_layout.addWidget(pi_disconnected_button, 1, 4)
        
        
        
        self.ardusub_label = QLabel('Ardusub Disconnected')
        self.ardusub_indicator = CircleIndicator(radius=10)
        self.ardusub_indicator.set_state(WidgetState.OFF)

        ardusub_connected_button = QPushButton()
        ardusub_connected_button.setText('Ardusub connected')
        ardusub_connected_button.clicked.connect(self.publish_ardusub_connected)

        ardusub_disconnected_button = QPushButton()
        ardusub_disconnected_button.setText('Ardusub disconnected')
        ardusub_disconnected_button.clicked.connect(self.publish_ardusub_disconnected)

        simulation_layout.addWidget(self.ardusub_label, 2, 1)
        simulation_layout.addWidget(self.ardusub_indicator, 2, 2)
        simulation_layout.addWidget(ardusub_connected_button, 2, 3)
        simulation_layout.addWidget(ardusub_disconnected_button, 2, 4)

        simulation_layout.setColumnStretch(1, 1)
        simulation_layout.setColumnStretch(2, 1)
        simulation_layout.setColumnStretch(3, 1)
        simulation_layout.setColumnStretch(4, 1)
        simulation_layout.setColumnStretch(5, 3)

        simulation_group.setLayout(simulation_layout)

        return simulation_group


    def publish_arm(self) -> None:
        payload = VehicleState(pi_connected = self.pi, ardusub_connected = self.ardusub, armed = True)
        print(payload)
        self.publisher.publish(payload)
        print("seeing if it published")


    def publish_disarm(self) -> None:
        payload = VehicleState(pi_connected = self.pi, ardusub_connected = self.ardusub, armed = False)
        print(payload)
        self.publisher.publish(payload)
        
    def publish_pi_connected(self) -> None:
        payload = VehicleState(pi_connected = True, ardusub_connected = self.ardusub, armed = self.armed)
        print(payload)
        self.publisher.publish(payload)
        print("seeing if it published")


    def publish_pi_disconnected(self) -> None:
        payload = VehicleState(pi_connected = False, ardusub_connected = self.ardusub, armed = self.armed)
        print(payload)
        self.publisher.publish(payload)


    def publish_ardusub_connected(self) -> None:
        payload = VehicleState(pi_connected = self.pi, ardusub_connected = True, armed = self.armed)
        print(payload)
        self.publisher.publish(payload)
        print("seeing if it published")


    def publish_ardusub_disconnected(self) -> None:
        payload = VehicleState(pi_connected = self.pi, ardusub_connected = False, armed = self.armed)
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
            GUINode().get_logger().error('Invalid port')

    @pyqtSlot(VehicleState)
    def refresh(self, msg: VehicleState) -> None:
            
        if msg.pi_connected:
            self.pi = True
            self.pi_label.setText('Pi connected')
            self.pi_indicator.set_state(WidgetState.ON)
        else:
            self.pi = False
            self.pi_label.setText('Pi disconnected')
            self.pi_indicator.set_state(WidgetState.OFF)
        if msg.ardusub_connected:
            self.ardusub = True
            self.ardusub_label.setText('Ardusub connected')
            self.ardusub_indicator.set_state(WidgetState.ON)
        else:
            self.ardusub = False
            self.ardusub_label.setText('Ardusub disconnected')
            self.ardusub_indicator.set_state(WidgetState.OFF)
            
        if msg.armed:
            self.armed = True
            self.armed_label.setText('Armed')
            self.arm_indicator.set_state(WidgetState.ON)
        else:
            self.armed = False
            self.armed_label.setText('Disarmed')
            self.arm_indicator.set_state(WidgetState.OFF)
       
        



