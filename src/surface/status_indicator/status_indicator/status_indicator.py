import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from std_msgs.msg import Bool

from rov_msgs.msg import VehicleState, Flooding

SIMULATION_CHANGE_VEHICLE_STATE = '/indicator/changeVehicleState'
SIMULATION_TOPIC_VEHICLE_STATE = '/indicator/vehicleState'
SIMULATION_TOPIC_ARM = '/indicator/arm'
SIMULATION_TOPIC_FLOODING = '/indicator/flooding'
SIMULATION_TOPIC_CHANGE_FLOODING = '/indicator/changeFlooding'

class StatusIndicatorNode(Node):
    armed = False
    pi_connected = True
    ardusub_connected = True
    flooding = False

    def __init__(self) -> None:
        super().__init__('status_indicator', parameter_overrides=[])

        self.simulation_param = self.declare_parameter('status-simulation', value=False).value

        self.vehicle_state_publisher = self.create_publisher(VehicleState,
                                            SIMULATION_TOPIC_VEHICLE_STATE,
                                            qos_profile_system_default)

        self.changed_vehicle_state_subscriber = self.create_subscription(VehicleState,
                                            SIMULATION_CHANGE_VEHICLE_STATE,
                                            self.change_vehicle_state_callback,
                                            qos_profile_system_default)

        self.flooding_publisher = self.create_publisher(Flooding,
                                            SIMULATION_TOPIC_FLOODING,
                                            qos_profile_system_default)

        self.changed_flooding_subscriber = self.create_subscription(Flooding,
                                            SIMULATION_TOPIC_CHANGE_FLOODING,
                                            self.change_flooding_callback,
                                            qos_profile_system_default)

        self.armed_subscriber = self.create_subscription(Bool, SIMULATION_TOPIC_ARM,
                                            self.arm_callback,
                                            qos_profile_system_default)


    def arm_callback(self, message: Bool) -> None:
        print(f'Armed: {message.data}')
        if self.ardusub_connected:
            self.armed = message.data
            new_message = VehicleState(pi_connected=self.pi_connected,
                                       ardusub_connected=self.ardusub_connected,
                                       armed=self.armed)
            self.vehicle_state_publisher.publish(new_message)

        print('Cannot change armed state while ardusub is disconnected')

    def change_vehicle_state_callback(self, message: VehicleState) -> None:
        print('Changing simulated vehicle state')
        self.pi_connected = message.pi_connected
        self.ardusub_connected = message.ardusub_connected

        if not message.pi_connected:
            self.ardusub_connected = False
        else:
            self.ardusub_connected = message.ardusub_connected

        if not self.ardusub_connected:
            self.armed = False
        else:
            self.armed = message.armed

        new_message = VehicleState(pi_connected=self.pi_connected,
                                   ardusub_connected=self.ardusub_connected, armed=self.armed)
        self.vehicle_state_publisher.publish(new_message)

    def change_flooding_callback(self, message: Flooding) -> None:
        print('Changing simulated flooding state')

        self.flooding = message.flooding

        new_message = Flooding(flooding=self.flooding)
        self.flooding_publisher.publish(new_message)


def main() -> None:
    rclpy.init()
    indicator_node = StatusIndicatorNode()

    if indicator_node.simulation_param:
        rclpy.spin(indicator_node)
    else:
        indicator_node.destroy_node()

if __name__ == '__main__':
    main()
