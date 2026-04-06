#!/usr/bin/env python3
import time
import json
import pigpio
import paho.mqtt.client as mqtt
import shelve
import colorsys
from typing import Any, Optional
import logging
from lamp_common import *

PIN_R: int = 19
PIN_G: int = 26
PIN_B: int = 13
PINS: list[int] = [PIN_R, PIN_G, PIN_B]
PWM_RANGE: int = 1000
PWM_FREQUENCY: int = 1000

LAMP_STATE_FILENAME: str = "lamp_state"

MQTT_CLIENT_ID: str = "indicator_service"

FP_DIGITS: int = 2

MAX_STARTUP_WAIT_SECS: float = 10.0


class InvalidLampConfig(Exception):
    pass


class LampDriver:

    def __init__(self) -> None:
        self._gpio: pigpio.pi = pigpio.pi()
        for color_pin in PINS:
            self._gpio.set_mode(color_pin, pigpio.OUTPUT)
            self._gpio.set_PWM_dutycycle(color_pin, 0)
            self._gpio.set_PWM_frequency(color_pin, PWM_FREQUENCY)
            self._gpio.set_PWM_range(color_pin, PWM_RANGE)

    def change_color(self, r: float, g: float, b: float) -> None:
        pins_values = zip(PINS, [r, g, b])
        for pin, value in pins_values:
            self._gpio.set_PWM_dutycycle(pin, value)


class LampService:
    def __init__(self) -> None:
        self.lamp_driver: LampDriver = LampDriver()
        self._client: mqtt.Client = self._create_and_configure_broker_client()
        self.armed = False
        self.write_current_settings_to_hardware()

    def _create_and_configure_broker_client(self) -> mqtt.Client:
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=MQTT_CLIENT_ID,
            protocol=MQTT_VERSION
        )
        client.will_set(client_state_topic(MQTT_CLIENT_ID), "0",
                        qos=2, retain=True)
        client.enable_logger()
        client.on_connect = self.on_connect
        client.message_callback_add(TOPIC_VEHICLE_STATE,
                                    self.on_message_vehicle_state)
        client.on_message = self.default_on_message
        logging.basicConfig(level = logging.DEBUG)
        return client

    def serve(self) -> None:
        start_time = time.time()
        while True:
            try:
                self._client.connect(MQTT_BROKER_HOST,
                                     port=MQTT_BROKER_PORT,
                                     keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
                print("Connected to broker")
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
            self._client.loop_forever()
        except Exception as e:
            print(e)

    def on_connect(self, client: mqtt.Client, userdata: Any,
                   flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode,
                   properties: Optional[mqtt.Properties]) -> None:
        print(f"Connected with reason code: {reason_code}")
        self._client.subscribe(TOPIC_VEHICLE_STATE, qos=1)

    def default_on_message(self, client: mqtt.Client, userdata: Any,
                           msg: mqtt.MQTTMessage) -> None:
        print("Received unexpected message on topic " +
              msg.topic + " with payload '" + str(msg.payload) + "'")

    def on_message_vehicle_state(self, client: mqtt.Client, userdata: Any,
                              msg: mqtt.MQTTMessage) -> None:
        try:
            new_config = msg.payload
            self.armed = bool(msg.payload[6])
            self.write_current_settings_to_hardware()
        except InvalidLampConfig:
            print("error applying new settings " + str(msg.payload))

    def get_current_armed(self) -> bool:
        return self.armed

    def set_current_armed(self, new_armed: bool) -> None:
        if new_armed not in [True, False]:
            raise InvalidLampConfig()
        self.write_current_settings_to_hardware()

    def write_current_settings_to_hardware(self) -> None:
        armed = self.armed
        if armed:
            self.lamp_driver.change_color(0, 255, 0)
        else:
            self.lamp_driver.change_color(255,0,0)

if __name__ == '__main__':
    LampService().serve()
