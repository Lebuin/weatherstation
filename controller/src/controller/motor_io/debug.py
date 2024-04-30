from __future__ import annotations

from dataclasses import dataclass

import pynput

from .. import motor as _motor
from .. import roof as _roof
from .base import MotorIO

__all__ = (
    'DebugIO',
)


@dataclass
class MotorConfig:
    key: str


class DebugIO(MotorIO):
    MotorConfig = MotorConfig
    Config = dict[_roof.Roof.Orientation, dict[_motor.Motor.Direction, MotorConfig]]
    Values = dict[_roof.Roof.Orientation, dict[_motor.Motor.Direction, bool]]

    config: Config

    keyboard_listener: pynput.keyboard.Listener
    pressed_keys: set

    values: Values = {
        _roof.Roof.Orientation.NORTH: {
            _motor.Motor.Direction.OPEN: False,
            _motor.Motor.Direction.CLOSE: False,
        },
        _roof.Roof.Orientation.SOUTH: {
            _motor.Motor.Direction.OPEN: False,
            _motor.Motor.Direction.CLOSE: False,
        },
    }


    def __init__(self, config: Config):
        self.config = config
        self.keyboard_listener = pynput.keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self.pressed_keys = set()
        self.keyboard_listener.start()


    def _on_key_press(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode | None) -> None:
        char = self._get_char(key)
        if type(char) == str:
            self.pressed_keys.add(char)

    def _on_key_release(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode | None) -> None:
        char = self._get_char(key)
        if type(char) == str:
            self.pressed_keys.remove(char)

    def _get_char(self, key: pynput.keyboard.Key | pynput.keyboard.KeyCode | None) -> str | None:
        return getattr(key, 'char', None)


    def _do_read(self, motor: _motor.Motor) -> bool:
        char = self.config[motor.orientation][motor.direction].key
        return char in self.pressed_keys


    def _do_write(self, motor: _motor.Motor, active: bool) -> None:
        self.values[motor.orientation][motor.direction] = active

