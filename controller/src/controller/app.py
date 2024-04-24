from __future__ import annotations

import logging
import sys

from . import config
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
        for motor in roof.motors.values():
            if motor.read():
                roof.do_movement(motor.direction, 1)


