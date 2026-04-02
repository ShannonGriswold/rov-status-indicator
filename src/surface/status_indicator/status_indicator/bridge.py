#!/home/shannongriswold/connected-devices/rov-status-indicator/.venv/bin/python
import logging
from typing import Any, Optional
import numpy as np
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.qos import qos_profile_system_default
from rov_msgs.msg import VehicleState
from std_msgs.msg import Bool
import time
import paho.mqtt.client as mqtt
#import paho

LOCAL_MQTT_CLIENT_ID = 'ros_node'
LOCAL_MQTT_BROKER_PORT: int = 1883
LOCAL_MQTT_BROKER_HOST: str = "localhost"

REMOTE_MQTT_CLIENT_ID = 'status_indicator'
REMOTE_MQTT_BROKER_HOST = '172.20.188.247'
REMOTE_MQTT_BROKER_PORT: int = 1883

MQTT_VERSION: mqtt.MQTTProtocolVersion = mqtt.MQTTv311
MQTT_BROKER_KEEP_ALIVE_SECS: int = 60
MAX_STARTUP_WAIT_SECS: float = 10.0

class BridgeNode(Node):
    def __init__(self) -> None:
        super().__init__('bridge', parameter_overrides=[])

        logging.basicConfig(level=logging.DEBUG)

        self.local_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=LOCAL_MQTT_CLIENT_ID,
            protocol=MQTT_VERSION
        )
        self.local_client.enable_logger()
        self.local_client.on_connect = self.local_on_connect
        self.local_client.message_callback_add('hiMqtt',
                                    self.on_message_publish_state)
        self.local_client.on_message = self.default_on_message

        self.remote_client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=REMOTE_MQTT_CLIENT_ID,
            protocol=MQTT_VERSION
        )
        self.remote_client.enable_logger()
        self.remote_client.on_connect = self.remote_on_connect
        self.remote_client.message_callback_add('rov/arm',
                                    self.on_message_recieve_arm)

        
        self.remote_client.on_message = self.default_on_message

        self.bridge()

    def bridge(self) -> None:
        start_time = time.time()
        while True:
            try:
                self.local_client.connect(LOCAL_MQTT_BROKER_HOST,
                                     port=LOCAL_MQTT_BROKER_PORT,
                                     keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
                print("Connected to local broker")
                self.remote_client.connect(REMOTE_MQTT_BROKER_HOST,
                                     port=REMOTE_MQTT_BROKER_PORT,
                                     keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
                print("Connected to remote broker")
                break
            except ConnectionRefusedError as e:
                current_time = time.time()
                delay = current_time - start_time
                if (delay) < MAX_STARTUP_WAIT_SECS:
                    print("Error connecting to broker; delaying and "
                          "will retry; delay={:.0f}".format(delay))
                    time.sleep(1)
                else:
                    raise e
        try:
            self.local_client.loop_start()
            self.remote_client.loop_forever()
        finally:
            print('errored')


    def local_on_connect(self, client: mqtt.Client, userdata: Any,
                   flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode,
                   properties: Optional[mqtt.Properties]) -> None:
        print(f'Connected with reason code: {reason_code}')

        self.local_client.subscribe('hiMqtt', qos=1)

    def remote_on_connect(self, client: mqtt.Client, userdata: Any,
                   flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode,
                   properties: Optional[mqtt.Properties]) -> None:
        print(f'Connected with reason code: {reason_code}')

        self.remote_client.subscribe('rov/arm', qos=1)

    def default_on_message(self, client: mqtt.Client, userdata: Any,
                           msg: mqtt.MQTTMessage) -> None:
        print('Received unexpected message on topic ' +
              msg.topic + " with payload '" + str(msg.payload) + "'")

    def on_message_publish_state(self, client: mqtt.Client, userdata: Any,
                              msg: mqtt.MQTTMessage) -> None:
        self.remote_client.publish('rov/vehicleState', msg.payload, qos=1)

    def on_message_recieve_arm(self, client: mqtt.Client, userdata: Any, 
                               msg: mqtt.MQTTMessage) -> None:
        self.local_client.publish('helloMqtt', msg.payload, qos=1)
        






def main() -> None:
    rclpy.init()
    bridge_node = BridgeNode()

    rclpy.spin(bridge_node)

if __name__ == '__main__':
    main()
