from kivy.app import App

from kivy.clock import Clock
import pigpio
from typing import Any, Optional
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label

import lampi_util

class IndicatorApp(App):

    gpio17_pressed = BooleanProperty(False)

    def on_start(self) -> None:
        self.set_up_gpio_and_network_status_popup()

    def set_up_gpio_and_network_status_popup(self) -> None:
        """Set up a popup to display the Lampi's IP
        address when a button is pressed."""
        self.pi: pigpio.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_gpio, 0.05)
        self.network_status_popup: Popup = self._build_network_status_popup()
        self.network_status_popup.bind(on_open=self.update_popup_ip_address)

    def _build_network_status_popup(self) -> Popup:
        return Popup(title='Network Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)

    def update_popup_ip_address(self, instance: Popup) -> None:
        """Update the popup with the current IP address"""
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        deviceid = lampi_util.get_device_id()
        msg = f"{interface}: {ipaddr}\nDeviceID: {deviceid}"
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
