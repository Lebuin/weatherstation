from __future__ import annotations

import enum

from controller import config, util

from .base import MotorIO

__all__ = (
    'MotorIO',
    'create',
)


def create(mode: util.Mode):
    if mode == util.Mode.GPIO:
        from .gpio import GPIO
        return GPIO(config.GPIO_CONFIG)
    elif mode == util.Mode.KEYBOARD:
        from .keyboard import KeyboardIO
        return KeyboardIO(config.KEYBOARD_IO_CONFIG)
    elif mode == util.Mode.MQTT:
        from .mqtt import MQTTIO
        return MQTTIO(config.MQTT_IO_CONFIG)
    else:
        raise Exception(f'Unknown mode: {mode}')
