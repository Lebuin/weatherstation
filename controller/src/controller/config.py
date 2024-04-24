from __future__ import annotations

from datetime import timedelta

from . import motor, motor_io, roof

mode = motor_io.Mode.GPIO

# The time between polling for inputs
poll_duration = timedelta(milliseconds=100)
# The number of seconds it takes to open/close a roof
roof_movement_duration = timedelta(seconds=5)


# The keyboard keys used to input in DEBUG mode
keys = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: 'a',
        motor.Motor.Direction.CLOSE: 'z',
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: 'k',
        motor.Motor.Direction.CLOSE: 'm',
    }
}


# The GPIO pins used to connect the input and output signals
input_pins = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: 2,
        motor.Motor.Direction.CLOSE: 4,
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: 6,
        motor.Motor.Direction.CLOSE: 8,
    }
}
output_pins = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: 3,
        motor.Motor.Direction.CLOSE: 5,
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: 7,
        motor.Motor.Direction.CLOSE: 9,
    }
}
