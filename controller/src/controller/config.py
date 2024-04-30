from __future__ import annotations

from datetime import timedelta

from . import motor, motor_io, roof
from .motor_io.gpio import GPIO
from .motor_io.keyboard import KeyboardIO
from .motor_io.mqtt import MQTTIO

MODE = motor_io.Mode.MQTT

# The time between polling for inputs
POLL_DURATION = timedelta(milliseconds=100)
# The number of seconds it takes to open/close a roof
ROOF_MOVEMENT_DURATION = timedelta(seconds=5)


MQTT_HOST = 'mosquitto'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'controller'
MQTT_USERNAME = 'controller'
MQTT_PASSWORD = 'Kl7sJuVJnZ33BtW'
MQTT_TOPIC_PREFIX = 'weatherstation'


# The keyboard keys used to input in DEBUG mode
KEYBOARD_IO_CONFIG = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: KeyboardIO.MotorConfig(key='a'),
        motor.Motor.Direction.CLOSE: KeyboardIO.MotorConfig(key='z'),
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: KeyboardIO.MotorConfig(key='k'),
        motor.Motor.Direction.CLOSE: KeyboardIO.MotorConfig(key='m'),
    },
}

MQTT_IO_CONFIG = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: MQTTIO.MotorConfig(topic='roof/north/open'),
        motor.Motor.Direction.CLOSE: MQTTIO.MotorConfig(topic='roof/north/close'),
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: MQTTIO.MotorConfig(topic='roof/south/open'),
        motor.Motor.Direction.CLOSE: MQTTIO.MotorConfig(topic='roof/south/close'),
    },
}


# The GPIO pins used to connect the input and output signals
# KEEP THESE IN SYNC WITH setup_pins.sh!
GPIO_CONFIG = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: GPIO.MotorConfig(
            input_pin=2,
            output_pin=3,
            pin_mode=GPIO.PinMode.ACTIVE_HIGH,
        ),
        motor.Motor.Direction.CLOSE: GPIO.MotorConfig(
            input_pin=4,
            output_pin=5,
            pin_mode=GPIO.PinMode.ACTIVE_HIGH,
        ),
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: GPIO.MotorConfig(
            input_pin=6,
            output_pin=7,
            pin_mode=GPIO.PinMode.ACTIVE_HIGH,
        ),
        motor.Motor.Direction.CLOSE: GPIO.MotorConfig(
            input_pin=8,
            output_pin=9,
            pin_mode=GPIO.PinMode.ACTIVE_HIGH,
        ),
    },
}
