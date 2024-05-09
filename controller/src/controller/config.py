from __future__ import annotations

from datetime import timedelta

from . import util
from .motor_io.gpio import GPIO
from .motor_io.keyboard import KeyboardIO
from .motor_io.mqtt import MQTTIO

MODE = util.Mode.GPIO

# Each roof has a position between 0 (closed) and 1 (fully opened). Each position step has a range
# of temperatures between which it is allowed. For example: if the roofs are at position .2, and
# the temperature is 24˚C, nothing will happens. As soon as the temperature rises above 25˚C, the
# roof opens to .5, where it will stay until the temperature rises further above 26˚C, or drops
# below 22˚C.
POSITION_STEPS = (
    util.PositionStep(0, float('-inf'), 25),
    util.PositionStep(.15, 23, 26),
    util.PositionStep(.35, 23.5, 27),
    util.PositionStep(1, 24, float('inf')),
)
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
ROOF_MOVEMENT_DURATION = timedelta(seconds=160)
# We can't measure the true position of a roof, so we rely on an estimate based on how long we've
# been actuating the motors. If the motors have been actuated outside of our own control, our
# estimate may be wildly off. So every few hours, when we expect the roof to be fully
# opened/closed, we let it move in that direction for ROOF_MOVEMENT_DURATION to be sure that it
# really is fully opened/closed, even if it wasn't before.
ROOF_VERIFICATION_INTERVAL = timedelta(hours=6)
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
MODE = util.Mode.MQTT
# WEATHER_REPORT_VALIDITY = timedelta(minutes=3)
# AUTO_MOVEMENT_CURFEW = timedelta(minutes=1)
# MANUAL_MOVEMENT_CURFEW = timedelta(minutes=2)
ROOF_MOVEMENT_DURATION = timedelta(seconds=10)
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
