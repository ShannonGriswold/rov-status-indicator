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

        simulation_layout.setColumnStretch(1, 1)
        simulation_layout.setColumnStretch(2, 1)
        simulation_layout.setColumnStretch(3, 1)
        simulation_layout.setColumnStretch(4, 1)
        simulation_layout.setColumnStretch(5, 3)

        simulation_group.setLayout(simulation_layout)

        return simulation_group


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
            GUINode().get_logger().error('Invalid port')

    @pyqtSlot(VehicleState)
    def refresh(self, msg: VehicleState) -> None:
        if msg.armed:
            self.armed = True
            self.armed_label.setText('Armed')
            self.arm_indicator.set_state(WidgetState.ON)
        else:
            self.armed = False
            self.armed_label.setText('Disarmed')
            self.arm_indicator.set_state(WidgetState.OFF)

