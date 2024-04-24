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
        motor.Motor.Direction.OPEN: 0,
        motor.Motor.Direction.CLOSE: 2,
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: 4,
        motor.Motor.Direction.CLOSE: 6,
    }
}
output_pins = {
    roof.Roof.Orientation.NORTH: {
        motor.Motor.Direction.OPEN: 1,
        motor.Motor.Direction.CLOSE: 3,
    },
    roof.Roof.Orientation.SOUTH: {
        motor.Motor.Direction.OPEN: 5,
        motor.Motor.Direction.CLOSE: 7,
    }
}
