#!/home/shannongriswold/connected-devices/rov-status-indicator/.venv/bin/python
import json

# Uncomment if using paho debug messages
# import logging
import time
from typing import Any

import paho
import paho.mqtt.client as mqtt
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from std_msgs.msg import Bool

from rov_msgs.msg import Flooding, VehicleState
from rov_msgs.srv import IpStatus, VehicleArming

SIMULATION_ROS_TOPICS = {
    'vehicleState': '/indicator/vehicleState',
    'flooding': '/indicator/flooding',
    'arm': '/indicator/arm',
}

REAL_ROS_TOPICS = {
    'vehicleState': 'vehicle_state_event',
    'flooding': 'flooding',
    'arm': 'arming'
}

ROS_TOPIC_ADD_STATUS_INDICATOR = 'addStatusIndicator'

MQTT_TOPIC_VEHICLE_STATE = 'rov/vehicleState'
MQTT_TOPIC_ARM = 'rov/arm'
MQTT_TOPIC_FLOODING = 'rov/flooding'

REMOTE_MQTT_CLIENT_ID = 'status_indicator'

MQTT_VERSION: paho.mqtt.enums.MQTTProtocolVersion = mqtt.MQTTv311
MQTT_BROKER_KEEP_ALIVE_SECS: int = 60
MAX_STARTUP_WAIT_SECS: float = 10.0



class BridgeNode(Node):

    def __init__(self) -> None:
        super().__init__('bridge', parameter_overrides=[])

        self.simulation_param = self.declare_parameter('status-simulation', value=False).value

        self.topics = SIMULATION_ROS_TOPICS if self.simulation_param else REAL_ROS_TOPICS

        # Uncomment to recieve paho debug messages
        # logging.basicConfig(level=logging.DEBUG)

        self.vehicle_state_subscriber = self.create_subscription(
            VehicleState,
            self.topics['vehicleState'],
            self.on_message_publish_state,
            qos_profile_system_default,
        )

        self.flooding_subscriber = self.create_subscription(
            Flooding,
            self.topics['flooding'],
            self.on_message_publish_flooding,
            qos_profile_system_default,
        )

        self.arm_publisher = self.create_publisher(
            Bool, self.topics['arm'], qos_profile_system_default
        )
        self.arm_client = self.create_client(VehicleArming, 'arming')

        self.remote_clients: list[mqtt.Client] = []

        self.ip_add_service = self.create_service(
            IpStatus, ROS_TOPIC_ADD_STATUS_INDICATOR, callback=self.ip_add_service_callback
        )

        self.most_recent_vehicle_state = {
            'armed': False,
            'pi_connected': False,
            'ardusub_connected': False
        }
        self.most_recent_flooding = {
            'flooding': False
        }

    def remote_on_connect(
        self,
        client: mqtt.Client,
        _userdata: Any,  # noqa: ANN401
        _flags: mqtt.ConnectFlags,
        reason_code: paho.mqtt.reasoncodes.ReasonCode,
        _properties: paho.mqtt.properties.Properties | None,
    ) -> None:
        self.get_logger().info(f'Connected with reason code: {reason_code}')

        client.publish(MQTT_TOPIC_VEHICLE_STATE,
                       json.dumps(self.most_recent_vehicle_state).encode('utf-8'), qos=1)
        client.publish(MQTT_TOPIC_FLOODING, json.dumps(self.most_recent_flooding).encode('utf-8'),
                       qos=1)

        client.subscribe(MQTT_TOPIC_ARM, qos=1)

    def connect_to_remote(self, remote_client: mqtt.Client, ip_addr: str, port: int) -> bool:
        start_time = time.time()
        while True:
            try:
                self.get_logger().info('trying to connect to remote broker')
                try:
                    remote_client.connect(ip_addr, port=port, keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
                except TimeoutError:
                    self.get_logger().error('Invalid ip address port pair, try again')
                    return False
                break
            except ConnectionRefusedError:
                current_time = time.time()
                delay = current_time - start_time
                if (delay) < MAX_STARTUP_WAIT_SECS:
                    self.get_logger().warning(
                        f'Error connecting to broker; delaying and will retry; delay={delay:.0f}'
                    )
                    time.sleep(1)
                else:
                    self.get_logger().error('Invalid ip address port pair, try again')
                    return False
        self.get_logger().info('Connected to remote broker')
        remote_client.loop_start()
        return True

    def ip_add_service_callback(
        self, request: IpStatus.Request, response: IpStatus.Response
    ) -> IpStatus.Response:
        client_id = REMOTE_MQTT_CLIENT_ID + str(len(self.remote_clients))
        remote_client = mqtt.Client(
            callback_api_version=paho.mqtt.enums.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=MQTT_VERSION,
        )
        remote_client.enable_logger()
        remote_client.on_connect = self.remote_on_connect
        remote_client.on_disconnect = self.remote_on_disconnect
        remote_client.message_callback_add(MQTT_TOPIC_ARM, self.on_message_recieve_arm)

        remote_client.on_message = self.default_on_message

        # self.remote_clients.append(remote_client)

        if self.connect_to_remote(remote_client, request.ip_address, request.port):
            self.remote_clients.append(remote_client)
            response.connected = True
        else:
            response.connected = False

        response.ip_address = request.ip_address
        response.port = request.port
        return response

    def remote_on_disconnect(
        self,
        client: mqtt.Client,
        _userdata: Any,  # noqa: ANN401
        _disconnect_flags: mqtt.DisconnectFlags,
        reason_code: paho.mqtt.reasoncodes.ReasonCode,
        _properties: paho.mqtt.properties.Properties | None,
    ) -> None:
        self.get_logger().warning(f'Disconnected with reason code: {reason_code}')
        client.reconnect()

    def default_on_message(
        self, _client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage  # noqa: ANN401
    ) -> None:
        self.get_logger().warning(
            'Received unexpected message on topic '
            + msg.topic
            + " with payload '"
            + str(msg.payload)
            + "'"
        )

    def on_message_publish_state(self, message: VehicleState) -> None:
        state = {
            'armed': message.armed,
            'ardusub_connected': message.ardusub_connected,
            'pi_connected': message.pi_connected,
        }

        self.most_recent_vehicle_state = state

        payload = json.dumps(state).encode('utf-8')

        for remote_client in self.remote_clients:
            remote_client.publish(MQTT_TOPIC_VEHICLE_STATE, payload, qos=1)

    def on_message_publish_flooding(self, message: Flooding) -> None:
        flooding = {
            'flooding': message.flooding,
        }

        self.most_recent_flooding = flooding

        payload = json.dumps(flooding).encode('utf-8')

        for remote_client in self.remote_clients:
            remote_client.publish(MQTT_TOPIC_FLOODING, payload, qos=1)

    def on_message_recieve_arm(
        self, _client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage  # noqa: ANN401
    ) -> None:
        message_value = None
        try:
            message = json.loads(msg.payload.decode('utf-8'))
            message_value = message['armed']
        except Exception:  # noqa: BLE001
            self.get_logger().error('Invalid arm message')
        if message_value is not None:
            if self.simulation_param:
                payload = Bool(data=message_value)
                self.arm_publisher.publish(payload)
            else:
                request = VehicleArming.Request(arm=message_value)
                response = self.arm_client.call(request)
                if not response or not response.message_sent:
                    self.get_logger().warning('Failed to arm or disarm')

def main() -> None:
    rclpy.init()
    bridge_node = BridgeNode()

    rclpy.spin(bridge_node)


if __name__ == '__main__':
    main()
