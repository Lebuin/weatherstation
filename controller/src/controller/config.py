from __future__ import annotations

from datetime import timedelta

from . import motor, motor_io, roof
from .motor_io.debug import DebugIO
from .motor_io.gpio import GPIO

mode = motor_io.Mode.DEBUG

# The time between polling for inputs
poll_duration = timedelta(milliseconds=100)
# The number of seconds it takes to open/close a roof
roof_movement_duration = timedelta(seconds=5)


# The keyboard keys used to input in DEBUG mode
key_config = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: DebugIO.MotorConfig(key='a'),
        motor.Motor.Direction.CLOSE: DebugIO.MotorConfig(key='z'),
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: DebugIO.MotorConfig(key='k'),
        motor.Motor.Direction.CLOSE: DebugIO.MotorConfig(key='m'),
    }
}


# The GPIO pins used to connect the input and output signals
# KEEP THESE IN SYNC WITH setup_pins.sh!
gpio_config = {
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
