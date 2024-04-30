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
    GPIO = 'gpio'
    DEBUG = 'debug'


def create(mode: Mode):
    if mode == Mode.GPIO:
        from .gpio import GPIO
        return GPIO(config.gpio_config)
    elif mode == Mode.DEBUG:
        from .debug import DebugIO
        return DebugIO(config.key_config)
    else:
        raise Exception(f'Unknown mode: {mode}')
