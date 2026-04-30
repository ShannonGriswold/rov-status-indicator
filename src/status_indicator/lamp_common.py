import paho.mqtt.client

DEVICE_ID_FILENAME = '/sys/class/net/eth0/address'

# MQTT Topic Names
TOPIC_VEHICLE_STATE: str = "rov/vehicleState"
TOPIC_ARM: str = "rov/arm"
TOPIC_FLOODING_STATE: str = "rov/flooding"
TOPIC_FLASH_FLOOD: str = "indicator/flashFlood"

def get_device_id() -> str:
    mac_addr = open(DEVICE_ID_FILENAME).read().strip()
    return mac_addr.replace(':', '')


def client_state_topic(client_id: str) -> str:
    return f'lamp/connection/{client_id}/state'


def broker_bridge_connection_topic() -> str:
    device_id = get_device_id()
    return f'$SYS/broker/connection/{device_id}_broker/state'


# MQTT Broker Connection info
MQTT_VERSION: int = paho.mqtt.client.MQTTv311
MQTT_BROKER_HOST: str = 'localhost'
MQTT_BROKER_PORT: int = 1883
MQTT_BROKER_KEEP_ALIVE_SECS: int = 60
