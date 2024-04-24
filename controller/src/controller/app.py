from __future__ import annotations

import logging
import sys

from . import config, motor
from . import motor_io as _motor_io
from . import roof
from .scheduler import scheduler

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

motor_io = _motor_io.create(config.mode)
roofs = {
    roof.Roof.Orientation.NORTH: roof.Roof(motor_io, roof.Roof.Orientation.NORTH),
    roof.Roof.Orientation.SOUTH: roof.Roof(motor_io, roof.Roof.Orientation.SOUTH),
}


def run():
    loop()
    scheduler.start_loop()


def loop():
    scheduler.delay(loop, config.poll_duration)

    for roof in roofs.values():
        motor_open = roof.motors[motor.Motor.Direction.OPEN]
        motor_close = roof.motors[motor.Motor.Direction.CLOSE]

        motor_open_input = motor_open.read()
        motor_close_input = motor_close.read()

        if motor_open_input and motor_close_input:
            pass
        elif motor_open_input:
            roof.open(1)
        elif motor_close_input:
            roof.close(1)


