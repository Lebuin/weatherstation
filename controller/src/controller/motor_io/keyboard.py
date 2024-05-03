from __future__ import annotations

import typing
from dataclasses import dataclass

from .. import util
from .base import MotorIO

if typing.TYPE_CHECKING:
    import pynput

__all__ = (
    'KeyboardIO',
)


@dataclass
class MovementConfig:
    key: str


class KeyboardIO(MotorIO):
    MovementConfig = MovementConfig
    Config = dict[util.Movement, MovementConfig]

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


    def read(self, movement: util.Movement) -> bool:
        char = self.config[movement].key
        return char in self.pressed_keys


    def write(self, movement: util.Movement, active: bool) -> None:
        # Do nothing
        pass
