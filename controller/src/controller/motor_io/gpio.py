from __future__ import annotations

import enum
from dataclasses import dataclass

import wiringpi

from .. import util
from .base import MotorIO

__all__ = (
    'GPIO',
)


class PinMode(enum.Enum):
    ACTIVE_HIGH = enum.auto()
    ACTIVE_LOW = enum.auto()

@dataclass
class MovementConfig:
    input_pin: int
    output_pin: int
    pin_mode: PinMode = PinMode.ACTIVE_HIGH


class GPIO(MotorIO):
    PinMode = PinMode
    MovementConfig = MovementConfig
    Config = dict[util.Movement, MovementConfig]

    config: Config


    def __init__(self, config: Config):
        self.config = config

        wiringpi.wiringPiSetup()
        # pullUpDnControl doesn't seem to work in wiringOP, so we set the pin modes in pin_mode.sh
        # instead.
        # for orientation in input_pins.keys():
        #     for direction in input_pins[orientation].keys():
        #         input_pin = self.input_pins[orientation][direction]
        #         output_pin = self.output_pins[orientation][direction]
        #         wiringpi.pinMode(input_pin, wiringpi.INPUT)
        #         wiringpi.pullUpDnControl(input_pin, wiringpi.PUD_DOWN)
        #         wiringpi.pinMode(output_pin, wiringpi.OUTPUT)


    def read(self, movement: util.Movement) -> bool:
        pin = self.config[movement].input_pin
        return wiringpi.digitalRead(pin) == 1


    def write(self, movement: util.Movement, active: bool) -> None:
        pin_config = self.config[movement]
        pin_value = int(bool(active) ^ (pin_config.pin_mode == PinMode.ACTIVE_LOW))
        wiringpi.digitalWrite(pin_config.output_pin, pin_value)
