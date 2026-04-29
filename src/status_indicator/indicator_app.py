import json
from kivy.app import App

from kivy.clock import Clock
import pigpio
from typing import Any, Optional
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import paho.mqtt.client as mqtt
from paho.mqtt.client import Client, CallbackAPIVersion
from lamp_common import *
from kivy.uix.gridlayout import *
from kivy.uix.button import *
import lampi_util
from kivy.graphics import Color
MQTT_CLIENT_ID = "lampi_ui"

class IndicatorApp(App):

    gpio17_pressed = BooleanProperty(False)
    arm_text = StringProperty("Disarmed")
    ardusub_text = StringProperty("Ardusub Disconnected")
    pi_text = StringProperty("Pi Disconnected")
    flooding_text = StringProperty("No Water Detected")
    armed = BooleanProperty(False)
    flooding = BooleanProperty(False)
    pi_connected = BooleanProperty(False)
    ardusub_connected = BooleanProperty(False)

    def on_start(self) -> None:
        self.mqtt: Client = Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=MQTT_CLIENT_ID
        )
        self.mqtt.enable_logger()
        self.mqtt.on_connect = self.on_connect

        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT,
                          keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()
        self.set_up_gpio_and_network_status_popup()

    def on_connect(self, client: Client, userdata: Any,
                   flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode,
                   properties: Optional[mqtt.Properties]) -> None:
        self.mqtt.message_callback_add(TOPIC_VEHICLE_STATE,
                                       self.receive_vehicle_state)
        self.mqtt.subscribe(TOPIC_VEHICLE_STATE, qos=1)
        self.mqtt.message_callback_add(TOPIC_FLOODING_STATE,
                                       self.receive_flooding_state)
        self.mqtt.subscribe(TOPIC_FLOODING_STATE, qos=1)

    def receive_vehicle_state(self, client: Client, userdata: Any,
                              message: mqtt.MQTTMessage) -> None:
        try:
            new_state = json.loads(message.payload.decode('utf-8'))
            Clock.schedule_once(lambda dt: self._update_ui(new_state), 0.01)
        except Exception:
            print('Invalid vehicle state')
    def receive_flooding_state(self, client: Client, userdata: Any,
                              message: mqtt.MQTTMessage) -> None:
        try:
            new_state = json.loads(message.payload.decode('utf-8'))
            Clock.schedule_once(lambda dt: self._update_ui_flooding(new_state), 0.01)
        except Exception:
            print('Invalid flooding state')


    def send_arm(self) -> None:
        state = {
            'armed': True
        }
        message = json.dumps(state).encode('utf-8')
        self.mqtt.publish(TOPIC_ARM, message, qos=1)

    def send_disarm(self) -> None:
        state = {
            'armed': False
        }
        message = json.dumps(state).encode('utf-8')
        self.mqtt.publish(TOPIC_ARM, message, qos=1)

    def _update_ui_flooding(self, new_state: dict[str, Any]) -> None:
        self.flooding = new_state['flooding']
        if new_state['flooding']:
            self.flooding_text = 'Water Detected'
            self.flooding_popup.open()

        else:
            self.flooding_text = 'No Water Detected'
            self.flooding_popup.dismiss()


    def _update_ui(self, new_state: dict[str, Any]) -> None:
        self.armed = new_state['armed']
        self.pi_connected = new_state['pi_connected']
        self.ardusub_connected = new_state['ardusub_connected']
        if new_state['armed']:
            self.arm_text = 'Armed'
        else:
            self.arm_text = 'Disarmed'
        if new_state['pi_connected']:
            self.pi_text = 'Pi Connected'
        else:
            self.pi_text = 'Pi Disconnected'
        if new_state['ardusub_connected']:
            self.ardusub_text = 'Ardusub Connected'
        else:
            self.ardusub_text = 'Ardusub Disconnected'

    def set_up_gpio_and_network_status_popup(self) -> None:
        """Set up a popup to display the Lampi's IP
        address when a button is pressed."""
        self.pi: pigpio.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_gpio, 0.05)
        self.network_status_popup: Popup = self._build_network_status_popup()
        self.network_status_popup.bind(on_open=self.update_popup_ip_address)
        self.flooding_popup: Popup = self._build_flooding_popup()

    def _build_network_status_popup(self) -> Popup:
        return Popup(title='Network Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)
    def _build_flooding_popup(self) -> Popup:
        layout = GridLayout(cols = 1, padding = 10)

        popupLabel = Label(text = "WATER DETECTED!", size_hint_y = 0.75)
        closeButton = Button(text = "Dismiss", size_hint_y = 0.25, background_normal='', background_color=(1,0,0,1))

        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)

        # Instantiate the modal popup and display
        popup = Popup(title ='Flooding Status',
                      content = layout,
                      size_hint =(1, 1), auto_dismiss=False)  
        # Attach close button press with popup.dismiss action
        closeButton.bind(on_press = self.press_button)
        return popup

    def press_button(self, instance):
        self.flooding_popup.dismiss()
        msg = {'flash': False}
        message = json.dumps(msg).encode('utf-8')
        print(f"publishing flass flood message: {message}")
        self.mqtt.publish(TOPIC_FLASH_FLOOD, message, qos=1)


    def update_popup_ip_address(self, instance: Popup) -> None:
        """Update the popup with the current IP address"""
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        deviceid = lampi_util.get_device_id()
        msg = f"{interface}: {ipaddr}\nDeviceID: {deviceid}"
        instance.content.text = msg

    def update_popUp_flooding(self, instance: Popup) -> None:
        msg = "WATER DETECTED!"
        instance.content.text = msg



    def on_gpio17_pressed(self, instance: Any, value: bool) -> None:
        """Open or close the popup depending on the provided value"""
        if value:
            self.network_status_popup.open()
        else:
            self.network_status_popup.dismiss()

    def _poll_gpio(self, _delta_time: float) -> None:
        # GPIO17 is the rightmost button when looking front of LAMPI
        self.gpio17_pressed = not self.pi.read(17)
