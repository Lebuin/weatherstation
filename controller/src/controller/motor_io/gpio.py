from __future__ import annotations

import wiringpi

from .. import motor as _motor
from .. import roof as _roof
from .base import MotorIO


class GPIO(MotorIO):
    PinConfig = dict[_roof.Roof.Orientation, dict[_motor.Motor.Direction, int]]

    input_pins: PinConfig
    output_pins: PinConfig

    _initialized = False


    def __init__(self, input_pins: PinConfig, output_pins: PinConfig):
        self.input_pins = input_pins
        self.output_pins = output_pins

        wiringpi.wiringPiSetup()
        # pullUpDnControl doesn't seem to work, so we set the pin modes in pin_mode.sh instead
        # for orientation in input_pins.keys():
        #     for direction in input_pins[orientation].keys():
        #         input_pin = self.input_pins[orientation][direction]
        #         output_pin = self.output_pins[orientation][direction]
        #         wiringpi.pinMode(input_pin, wiringpi.INPUT)
        #         wiringpi.pullUpDnControl(input_pin, wiringpi.PUD_DOWN)
        #         wiringpi.pinMode(output_pin, wiringpi.OUTPUT)


    def _do_read(self, motor: _motor.Motor) -> bool:
        # Temporarily disable all motors except NORTH:OPEN
        if (
            motor.orientation == _roof.Roof.Orientation.SOUTH
            or motor.direction == _motor.Motor.Direction.CLOSE
        ):
            return False
        pin = self.input_pins[motor.orientation][motor.direction]
        return wiringpi.digitalRead(pin) == 1


    def _do_write(self, motor: _motor.Motor, value: bool) -> None:
        pin = self.output_pins[motor.orientation][motor.direction]
        wiringpi.digitalWrite(pin, 1 if value else 0)
