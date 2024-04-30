from __future__ import annotations

import enum

from controller import config

from .base import MotorIO

__all__ = (
    'MotorIO',
    'Mode',
    'create',
)


class Mode(enum.Enum):
    GPIO = enum.auto()
    KEYBOARD = enum.auto()
    MQTT = enum.auto()


def create(mode: Mode):
    if mode == Mode.GPIO:
        from .gpio import GPIO
        return GPIO(config.GPIO_CONFIG)
    elif mode == Mode.KEYBOARD:
        from .keyboard import KeyboardIO
        return KeyboardIO(config.KEYBOARD_IO_CONFIG)
    elif mode == Mode.MQTT:
        from .mqtt import MQTTIO
        return MQTTIO(config.MQTT_IO_CONFIG)
    else:
        raise Exception(f'Unknown mode: {mode}')
