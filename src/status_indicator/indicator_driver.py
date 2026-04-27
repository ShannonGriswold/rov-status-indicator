import warnings

# Allow debugging on systems without pigpio
# If not has_pigpio, LampDriver won't actually do anything
has_pigpio: bool = True
try:
    import pigpio
except ImportError:
    warnings.warn('Could not find pigpio library; mocking LampDriver for testing', ImportWarning)
    has_pigpio = False

PWM_FREQUENCY = 1000
PWM_RANGE = 1000

RED_GPIO = 19
GREEN_GPIO = 26
BLUE_GPIO = 13
CHANNEL_PINS = [RED_GPIO, GREEN_GPIO, BLUE_GPIO]


class LampDriver:
    def __init__(self) -> None:
        """Create a LampDriver and set up pigpio.
        Silently skips setup if pigpio is not found.
        """
        if not has_pigpio:
            return

        self.pi = pigpio.pi()

        if not self.pi.connected:
            return

        for pin in CHANNEL_PINS:
            self.pi.set_PWM_frequency(pin, PWM_FREQUENCY)
            self.pi.set_PWM_range(pin, PWM_RANGE)
            self.pi.set_PWM_dutycycle(pin, 0)

    def set_lamp_armed(self) -> None:
        if not has_pigpio or not self.pi.connected:
            warnings.warn(RuntimeWarning)
            return
        rgb = [0, 0, 0]
        full_brightness_rgb = [0, 255, 0]
        for c, channel in enumerate(full_brightness_rgb):
            rgb[c] = channel

        for c, pin in enumerate(CHANNEL_PINS):
            self.pi.set_PWM_dutycycle(pin, rgb[c] * PWM_RANGE)

    def set_lamp_disarmed(self) -> None:
        if not has_pigpio or not self.pi.connected:
            warnings.warn(RuntimeWarning)
            return
        rgb = [0, 0, 0]
        full_brightness_rgb = [255, 0, 0]
        for c, channel in enumerate(full_brightness_rgb):
            rgb[c] = channel

        for c, pin in enumerate(CHANNEL_PINS):
            self.pi.set_PWM_dutycycle(pin, rgb[c] * PWM_RANGE)
