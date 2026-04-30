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
from gui.widgets.logger import Logger
from rov_msgs.msg import Flooding, VehicleState
from rov_msgs.srv import IpStatus

TOPIC_CHANGE_VEHICLE_STATE = '/indicator/changeVehicleState'
TOPIC_VEHICLE_STATE = '/indicator/vehicleState'
TOPIC_ADD_STATUS_INDICATOR = 'addStatusIndicator'
TOPIC_CHANGE_FLOODING = '/indicator/changeFlooding'
TOPIC_FLOODING = '/indicator/flooding'


WEB_HOST = 'ec2-98-90-18-209.compute-1.amazonaws.com'
WEB_PORT = 50001

class IndicatorTab(QWidget):
    signal = pyqtSignal(VehicleState)
    flooding_signal = pyqtSignal(Flooding)
    command_response_signal = pyqtSignal(IpStatus.Response)

    def __init__(self, simulation:bool) -> None:
        super().__init__()

        self.armed = False
        self.pi = False
        self.ardusub = False
        self.signal.connect(self.refresh)
        self.flooding_signal.connect(self.refresh_flooding)

        GUINode().create_signal_subscription(VehicleState, TOPIC_VEHICLE_STATE, self.signal)
        self.vehicle_state_publisher = GUINode().create_publisher(
            VehicleState, TOPIC_CHANGE_VEHICLE_STATE, qos_profile_system_default
        )
       
        self.flooding_publisher = GUINode().create_publisher(
            Flooding, TOPIC_CHANGE_FLOODING, qos_profile_system_default
        )

        GUINode().create_signal_subscription(Flooding, TOPIC_FLOODING, self.flooding_signal)

        root_layout = QVBoxLayout()
        root_layout.addWidget(self.create_indicator_group())

        bottom_layout = QHBoxLayout()

        if simulation:
            bottom_layout.addWidget(self.create_simulation_group())

        bottom_layout.addWidget(Logger())

        root_layout.addLayout(bottom_layout)

        root_layout.addStretch()
        self.setLayout(root_layout)
        
        self.command_response_signal.connect(self.ip_connection_status)

        self.ip_client = GUINode().create_client_multithreaded(IpStatus, TOPIC_ADD_STATUS_INDICATOR)

        self.ip_client.wait_for_service()
        # Add the ec2 by default on start
        self.add_ip(WEB_HOST, WEB_PORT)
        
        
        
       

    
    @pyqtSlot(IpStatus.Response)
    def arm_status(self, res: IpStatus.Response) -> None:
        if res.message_sent:
            return True
        else:
            return False
            

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
        ip_button.clicked.connect(self.add_ip_button_callback)

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

        self.arm_button = QPushButton()
        self.arm_button.setText('ARM')
        self.arm_button.clicked.connect(self.publish_arm)
        self.arm_button.setDisabled(True)

        self.disarm_button = QPushButton()
        self.disarm_button.setText('DISARM')
        self.disarm_button.clicked.connect(self.publish_disarm)
        self.disarm_button.setDisabled(True)

        simulation_layout.addWidget(self.armed_label, 0, 1)
        simulation_layout.addWidget(self.arm_indicator, 0, 2)
        simulation_layout.addWidget(self.arm_button, 0, 3)
        simulation_layout.addWidget(self.disarm_button, 0, 4)

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

        self.ardusub_connected_button = QPushButton()
        self.ardusub_connected_button.setText('Ardusub connected')
        self.ardusub_connected_button.clicked.connect(self.publish_ardusub_connected)
        self.ardusub_connected_button.setDisabled(True)

        self.ardusub_disconnected_button = QPushButton()
        self.ardusub_disconnected_button.setText('Ardusub disconnected')
        self.ardusub_disconnected_button.clicked.connect(self.publish_ardusub_disconnected)
        self.ardusub_disconnected_button.setDisabled(True)

        simulation_layout.addWidget(self.ardusub_label, 2, 1)
        simulation_layout.addWidget(self.ardusub_indicator, 2, 2)
        simulation_layout.addWidget(self.ardusub_connected_button, 2, 3)
        simulation_layout.addWidget(self.ardusub_disconnected_button, 2, 4)

        self.flooding_label = QLabel('No Water Detected')
        self.flooding_indicator = CircleIndicator(radius=10)
        self.flooding_indicator.set_state(WidgetState.ON)

        flooding_detected_button = QPushButton()
        flooding_detected_button.setText('Flooding Detected')
        flooding_detected_button.clicked.connect(self.publish_flooding_detected)

        flooding_not_detected_button = QPushButton()
        flooding_not_detected_button.setText('Flooding Not Detected')
        flooding_not_detected_button.clicked.connect(self.publish_flooding_not_detected)

        simulation_layout.addWidget(self.flooding_label, 3, 1)
        simulation_layout.addWidget(self.flooding_indicator, 3, 2)
        simulation_layout.addWidget(flooding_not_detected_button, 3, 3)
        simulation_layout.addWidget(flooding_detected_button, 3, 4)

        simulation_layout.setColumnStretch(1, 1)
        simulation_layout.setColumnStretch(2, 1)
        simulation_layout.setColumnStretch(3, 1)
        simulation_layout.setColumnStretch(4, 1)

        simulation_group.setLayout(simulation_layout)

        return simulation_group

    def publish_arm(self) -> None:
        payload = VehicleState(pi_connected=self.pi, ardusub_connected=self.ardusub, armed=True)
        self.vehicle_state_publisher.publish(payload)

    def publish_disarm(self) -> None:
        payload = VehicleState(pi_connected=self.pi, ardusub_connected=self.ardusub, armed=False)
        self.vehicle_state_publisher.publish(payload)

    def publish_pi_connected(self) -> None:
        payload = VehicleState(pi_connected=True, ardusub_connected=self.ardusub, armed=self.armed)
        self.vehicle_state_publisher.publish(payload)

    def publish_pi_disconnected(self) -> None:
        payload = VehicleState(pi_connected=False, ardusub_connected=self.ardusub, armed=self.armed)
        self.vehicle_state_publisher.publish(payload)

    def publish_ardusub_connected(self) -> None:
        payload = VehicleState(pi_connected=self.pi, ardusub_connected=True, armed=self.armed)
        self.vehicle_state_publisher.publish(payload)

    def publish_ardusub_disconnected(self) -> None:
        payload = VehicleState(pi_connected=self.pi, ardusub_connected=False, armed=self.armed)
        self.vehicle_state_publisher.publish(payload)

    def publish_flooding_detected(self) -> None:
        payload = Flooding(flooding=True)
        self.flooding_publisher.publish(payload)

    def publish_flooding_not_detected(self) -> None:
        payload = Flooding(flooding=False)
        self.flooding_publisher.publish(payload)

    def add_ip_button_callback(self) -> None:
        ip_input = self.input.text()
        try:
            port_number = int(self.port_input.text())
            self.add_ip(ip_input, port_number)
        except (TypeError, ValueError):
            GUINode().get_logger().error('Invalid port')
    
    @pyqtSlot(IpStatus.Response)
    def ip_connection_status(self, res: IpStatus.Response) -> None:
        if  res.connected:
            ip_item = QListWidgetItem(f'IP Address: {res.ip_address} \tPort: {res.port}')
            self.listWidget.addItem(ip_item)
            

    def add_ip(self, ip:str, port:int) -> None:
        GUINode().send_request_multithreaded(
                self.ip_client, IpStatus.Request(ip_address=ip, port=port), self.command_response_signal
        )

    @pyqtSlot(VehicleState)
    def refresh(self, msg: VehicleState) -> None:
        if msg.pi_connected:
            self.pi = True
            self.pi_label.setText('Pi connected')
            self.pi_indicator.set_state(WidgetState.ON)
            self.ardusub_connected_button.setDisabled(False)
            self.ardusub_disconnected_button.setDisabled(False)
        else:
            self.pi = False
            self.pi_label.setText('Pi disconnected')
            self.pi_indicator.set_state(WidgetState.OFF)
            self.ardusub_connected_button.setDisabled(True)
            self.ardusub_disconnected_button.setDisabled(True)
        if msg.ardusub_connected:
            self.ardusub = True
            self.ardusub_label.setText('Ardusub connected')
            self.ardusub_indicator.set_state(WidgetState.ON)
            self.arm_button.setDisabled(False)
            self.disarm_button.setDisabled(False)
        else:
            self.ardusub = False
            self.ardusub_label.setText('Ardusub disconnected')
            self.ardusub_indicator.set_state(WidgetState.OFF)
            self.arm_button.setDisabled(True)
            self.disarm_button.setDisabled(True)

        if msg.armed:
            self.armed = True
            self.armed_label.setText('Armed')
            self.arm_indicator.set_state(WidgetState.ON)
        else:
            self.armed = False
            self.armed_label.setText('Disarmed')
            self.arm_indicator.set_state(WidgetState.OFF)

    def refresh_flooding(self, msg: Flooding) -> None:
        if msg.flooding:
            self.flooding_label.setText('Water Detected')
            self.flooding_indicator.set_state(WidgetState.OFF)
        else:
            self.flooding_label.setText('No water detected')
            self.flooding_indicator.set_state(WidgetState.ON)
