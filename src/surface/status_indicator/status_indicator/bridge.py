#!/home/shannongriswold/connected-devices/rov-status-indicator/.venv/bin/python
import json
import logging
import time
from typing import Any, Optional

import paho.mqtt.client as mqtt
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from std_msgs.msg import Bool

from rov_msgs.msg import VehicleState

ROS_TOPIC_VEHICLE_STATE = '/hi'
ROS_TOPIC_FLOODING = 'flooding'
ROS_TOPIC_ARM = '/hello'

MQTT_TOPIC_VEHICLE_STATE = 'rov/vehicleState'
MQTT_TOPIC_ARM = 'rov/arm'
MQTT_TOPIC_FLOODING = 'rov/flooding'

REMOTE_MQTT_CLIENT_ID = 'status_indicator'
REMOTE_MQTT_BROKER_HOST = '172.20.113.144'
REMOTE_MQTT_BROKER_PORT: int = 1883

MQTT_VERSION: mqtt.MQTTProtocolVersion = mqtt.MQTTv311
MQTT_BROKER_KEEP_ALIVE_SECS: int = 60
MAX_STARTUP_WAIT_SECS: float = 10.0

class BridgeNode(Node):
    def __init__(self) -> None:
        super().__init__('bridge', parameter_overrides=[])

        logging.basicConfig(level=logging.DEBUG)

        self.vehicle_state_subscriber = self.create_subscription(VehicleState,
                ROS_TOPIC_VEHICLE_STATE, self.on_message_publish_state, qos_profile_system_default)

        self.arm_publisher = self.create_publisher(Bool, ROS_TOPIC_ARM, qos_profile_system_default)

        self.remote_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=REMOTE_MQTT_CLIENT_ID,
            protocol=MQTT_VERSION
        )
        self.remote_client.enable_logger()
        self.remote_client.on_connect = self.remote_on_connect
        self.remote_client.on_disconnect = self.remote_on_disconnect
        self.remote_client.message_callback_add(MQTT_TOPIC_ARM,
                                    self.on_message_recieve_arm)

        self.remote_client.on_message = self.default_on_message

        self.connect_to_remote()

    def remote_on_connect(self, _client: mqtt.Client, _userdata: Any,
                   _flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode,
                   _properties: Optional[mqtt.Properties]) -> None:
        print(f'Connected with reason code: {reason_code}')

        self.remote_client.subscribe(MQTT_TOPIC_ARM, qos=1)

    def connect_to_remote(self) -> None:
        start_time = time.time()
        while True:
            try:
                self.remote_client.connect(REMOTE_MQTT_BROKER_HOST,
                                     port=REMOTE_MQTT_BROKER_PORT,
                                     keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
                print('Connected to remote broker')
                break
            except ConnectionRefusedError as e:
                current_time = time.time()
                delay = current_time - start_time
                if (delay) < MAX_STARTUP_WAIT_SECS:
                    print('Error connecting to broker; delaying and '
                          f'will retry; delay={delay:.0f}')
                    time.sleep(1)
                else:
                    raise e
        try:
            self.remote_client.loop_start()
        finally:
            print('errored')

    def remote_on_disconnect(self, _client: mqtt.Client, _userdata: Any, 
                    _disconnect_flags: mqtt.DisconnectFlags, reason_code: mqtt.ReasonCode, 
                    _properties: Optional[mqtt.Properties]) -> None:
        print(f'Disconnected with reason code: {reason_code}')
        self.connect_to_remote()

    def default_on_message(self, _client: mqtt.Client, _userdata: Any,
                           msg: mqtt.MQTTMessage) -> None:
        print('Received unexpected message on topic ' +
              msg.topic + " with payload '" + str(msg.payload) + "'")

    def on_message_publish_state(self, message: VehicleState) -> None:
        state = {
            'armed': message.armed,
            'ardusub_connected': message.ardusub_connected,
            'pi_connected': message.pi_connected,
        }

        payload = json.dumps(state).encode('utf-8')

        self.remote_client.publish(MQTT_TOPIC_VEHICLE_STATE, payload, qos=1, retain=True)

    def on_message_recieve_arm(self, _client: mqtt.Client, _userdata: Any, 
                               msg: mqtt.MQTTMessage) -> None:
        try:
            message = json.loads(msg.payload.decode('utf-8'))
            payload = Bool(message.armed)
            self.arm_publisher.publish(payload)
        except Exception:
            print('Invalid arm message')

def main() -> None:
    rclpy.init()
    bridge_node = BridgeNode()

    rclpy.spin(bridge_node)

if __name__ == '__main__':
    main()
