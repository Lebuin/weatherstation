from __future__ import annotations

import typing
from dataclasses import dataclass

from .. import motor as _motor
from .. import roof as _roof
from .base import MotorIO

if typing.TYPE_CHECKING:
    import pynput

__all__ = (
    'KeyboardIO',
)


@dataclass
class MotorConfig:
    key: str


class KeyboardIO(MotorIO):
    MotorConfig = MotorConfig
    Config = dict[_roof.Roof.Orientation, dict[_motor.Motor.Direction, MotorConfig]]

    config: Config

    keyboard_listener: pynput.keyboard.Listener
    pressed_keys: set


    def __init__(self, config: Config):
        import pynput

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
        # Do nothing
        pass
