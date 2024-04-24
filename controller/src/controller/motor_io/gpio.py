from __future__ import annotations

import wiringpi

from .. import motor, roof
from .base import MotorIO


class GPIO(MotorIO):
    PinConfig = dict[roof.Roof.Orientation, dict[motor.Motor.Direction, int]]

    input_pins: PinConfig
    output_pins: PinConfig

    _initialized = False


    def __init__(self, input_pins: PinConfig, output_pins: PinConfig):
        self.input_pins = input_pins
        self.output_pins = output_pins

        wiringpi.wiringPiSetup()
        for orientation in input_pins.keys():
            for direction in input_pins[orientation].keys():
                wiringpi.pinMode(self.input_pins[orientation][direction], wiringpi.INPUT)
                wiringpi.pinMode(self.output_pins[orientation][direction], wiringpi.OUTPUT)


    def _do_read(self, motor: motor.Motor) -> bool:
        pin = self.input_pins[motor.orientation][motor.direction]
        return wiringpi.digitalRead(pin) == 1


    def _do_write(self, motor: motor.Motor, value: bool) -> None:
        pin = self.output_pins[motor.orientation][motor.direction]
        wiringpi.digitalWrite(pin, 1 if value else 0)
