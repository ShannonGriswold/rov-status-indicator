import numpy as np
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.qos import qos_profile_system_default
from rov_msgs.msg import VehicleState
from std_msgs.msg import Bool
import time


class StatusIndicatorNode(Node):
    def __init__(self) -> None:
        super().__init__('status_indicator', parameter_overrides=[])

        self.publisher = self.create_publisher(VehicleState, '/hi', qos_profile_system_default)
        # self.publisher = self.create_publisher(Bool, '/testBool', qos_profile_system_default)

        self.subscriber = self.create_subscription(Bool, '/hello', self.arm_callback, qos_profile_system_default)

        while True:
            self.publish_messages()

    def arm_callback(self, message: Bool) -> None:
        print(f'Armed: {message.data}')

    def publish_messages(self) -> None:
        # message = Bool(data=True)
        # self.publisher.publish(message)
        # print("True")

        # time.sleep(3)

        # message = Bool(data=False)
        # self.publisher.publish(message)
        # print("False")

        # time.sleep(3)


        state = VehicleState(pi_connected=False, ardusub_connected=False, armed=False)
        self.publisher.publish(state)

        print('Pi Connected: 0, Ardusub Connected: 0 Armed: 0')

        time.sleep(3)

        state = VehicleState(pi_connected=True, ardusub_connected=False, armed=False)
        self.publisher.publish(state)

        print('Pi Connected: 1, Ardusub Connected: 0 Armed: 0')

        time.sleep(3)

        state = VehicleState(pi_connected=False, ardusub_connected=True, armed=False)
        self.publisher.publish(state)

        print('Pi Connected: 0, Ardusub Connected: 1 Armed: 0')

        time.sleep(3)

        state = VehicleState(pi_connected=False, ardusub_connected=False, armed=True)
        self.publisher.publish(state)

        print('Pi Connected: 0, Ardusub Connected: 0 Armed: 1')

        time.sleep(3)


def main() -> None:
    rclpy.init()
    indicator_node = StatusIndicatorNode()

    rclpy.spin(indicator_node)

if __name__ == '__main__':
    main()
