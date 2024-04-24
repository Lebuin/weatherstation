from __future__ import annotations

import pynput

from .. import motor, roof
from .base import MotorIO


class DebugIO(MotorIO):
    KeyConfig = dict[roof.Roof.Orientation, dict[motor.Motor.Direction, str]]
    Values = dict[roof.Roof.Orientation, dict[motor.Motor.Direction, bool]]

    key_config: KeyConfig

    keyboard_listener: pynput.keyboard.Listener
    pressed_keys: set

    values: Values = {
        roof.Roof.Orientation.NORTH: {
            motor.Motor.Direction.OPEN: False,
            motor.Motor.Direction.CLOSE: False,
        },
        roof.Roof.Orientation.SOUTH: {
            motor.Motor.Direction.OPEN: False,
            motor.Motor.Direction.CLOSE: False,
        },
    }


    def __init__(self, key_config: KeyConfig):
        self.key_config = key_config
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


    def _do_read(self, motor: motor.Motor) -> bool:
        char = self.key_config[motor.orientation][motor.direction]
        return char in self.pressed_keys


    def _do_write(self, motor: motor.Motor, value: bool) -> None:
        self.values[motor.orientation][motor.direction] = value

