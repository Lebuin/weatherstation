from __future__ import annotations

from datetime import timedelta

from . import util
from .motor_io.gpio import GPIO
from .motor_io.keyboard import KeyboardIO
from .motor_io.mqtt import MQTTIO

MODE = util.Mode.GPIO

# We want to keep the temperature inside the greenhouse between these values
MIN_INDOOR_TEMPERATURE = 20  # ˚C
MAX_INDOOR_TEMPERATURE = 25  # ˚C
# If the temperature inside the greenhouse is too high/low, we will open/close the roofs in steps
# of AUTO_MOVEMENT_FRACTION, and wait for AUTO_MOVEMENT_CURFEW between actions. So if the fraction
# is .2 and the curfew is 5 minutes, it takes at least 25 minutes to fully open/close the roofs.
AUTO_MOVEMENT_FRACTION = .2
AUTO_MOVEMENT_CURFEW = timedelta(minutes=5)
# When someone interacts with the roofs manually, we wait a while before responding to low/high
# temperatures again.
MANUAL_MOVEMENT_CURFEW = timedelta(hours=1)
# When we measure high winds outside the greenhouse, we fully close the roofs, and wait for
# HIGH_WIND_CURFEW to be sure that the "storm" has passed before monitoring the temperature again
# and possibly opening the roofs as a result.
HIGH_WIND = 40  # km/h
HIGH_WIND_CURFEW = timedelta(hours=1)
# If the last weather report is older than this, we assume the weather station is offline. Since
# we can't know the outside windspeed anymore, we have to assume the worst and fully close the
# roofs until we get another weather report.
WEATHER_REPORT_VALIDITY = timedelta(minutes=30)

# The time between application ticks
TICK_INTERVAL = timedelta(milliseconds=100)
# The number of seconds it takes to open/close a roof
ROOF_MOVEMENT_DURATION = timedelta(seconds=60)
# We periodically send a ping to healthchecks.io to let it know the script is still running. If
# healthchecks.io doesn't get an update from us for x amount of time, it will notify people on
# their phones. In known emergency situations, we explicitly send a nonzero status.
HEALTHCHECK_INTERVAL = timedelta(minutes=5)
HEALTHCHECK_URL = 'https://hc-ping.com/9ce41add-4bd4-484b-95f5-a27312fcde0f'


MQTT_HOST = 'mosquitto'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'controller'
MQTT_USERNAME = 'controller'
MQTT_PASSWORD = 'Kl7sJuVJnZ33BtW'
MQTT_TOPIC_PREFIX = 'weatherstation'
MQTT_REPORT_TOPIC = 'report'


# Debug values
# WEATHER_REPORT_VALIDITY = timedelta(minutes=3)
# AUTO_MOVEMENT_CURFEW = timedelta(minutes=1)
# MANUAL_MOVEMENT_CURFEW = timedelta(minutes=2)
# TICK_INTERVAL = timedelta(seconds=1)
# ROOF_MOVEMENT_DURATION = timedelta(seconds=10)
# HEALTHCHECK_INTERVAL = timedelta(minutes=1)


# The keyboard keys used to input in DEBUG mode
KEYBOARD_IO_CONFIG = {
    util.Movement(util.Orientation.NORTH, util.Direction.OPEN): KeyboardIO.MovementConfig(key='a'),
    util.Movement(util.Orientation.NORTH, util.Direction.CLOSE): KeyboardIO.MovementConfig(key='z'),
    util.Movement(util.Orientation.SOUTH, util.Direction.OPEN): KeyboardIO.MovementConfig(key='k'),
    util.Movement(util.Orientation.SOUTH, util.Direction.CLOSE): KeyboardIO.MovementConfig(key='m'),
}

MQTT_IO_CONFIG = {
    util.Movement(util.Orientation.NORTH, util.Direction.OPEN): MQTTIO.MovementConfig(topic='roof/north/open'),
    util.Movement(util.Orientation.NORTH, util.Direction.CLOSE): MQTTIO.MovementConfig(topic='roof/north/close'),
    util.Movement(util.Orientation.SOUTH, util.Direction.OPEN): MQTTIO.MovementConfig(topic='roof/south/open'),
    util.Movement(util.Orientation.SOUTH, util.Direction.CLOSE): MQTTIO.MovementConfig(topic='roof/south/close'),
}


# The GPIO pins used to connect the input and output signals
# KEEP THESE IN SYNC WITH setup_pins.sh!
GPIO_CONFIG = {
    util.Movement(util.Orientation.NORTH, util.Direction.OPEN): GPIO.MovementConfig(
        input_pin=2,
        output_pin=3,
        pin_mode=GPIO.PinMode.ACTIVE_HIGH,
    ),
    util.Movement(util.Orientation.NORTH, util.Direction.CLOSE): GPIO.MovementConfig(
        input_pin=4,
        output_pin=5,
        pin_mode=GPIO.PinMode.ACTIVE_LOW,
    ),
    util.Movement(util.Orientation.SOUTH, util.Direction.OPEN): GPIO.MovementConfig(
        input_pin=6,
        output_pin=7,
        pin_mode=GPIO.PinMode.ACTIVE_HIGH,
    ),
    util.Movement(util.Orientation.SOUTH, util.Direction.CLOSE): GPIO.MovementConfig(
        input_pin=8,
        output_pin=9,
        pin_mode=GPIO.PinMode.ACTIVE_LOW,
    ),
}
