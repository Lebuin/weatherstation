from __future__ import annotations

import logging
import sys

from . import config, motor
from . import motor_io as _motor_io
from . import roof as _roof
from .scheduler import scheduler

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

motor_io = _motor_io.create(config.mode)
roofs = {
    _roof.Roof.Orientation.NORTH: _roof.Roof(motor_io, _roof.Roof.Orientation.NORTH),
    _roof.Roof.Orientation.SOUTH: _roof.Roof(motor_io, _roof.Roof.Orientation.SOUTH),
}

# We only want each input press to be handled once, so we keep track of which ones we've
# already sent.
input_handled: set[motor.Motor] = set()


def run():
    loop()
    scheduler.start_loop()


def loop():
    scheduler.delay(loop, config.poll_duration)

    for roof in roofs.values():
        for direction, motor in roof.motors.items():
            input_ = motor.read()
            opposite_input = roof.motors[direction.opposite].read()

            if not input_:
                input_handled.discard(motor)

            elif not opposite_input and motor not in input_handled:
                input_handled.add(motor)

                if roof.state == _roof.Roof.State.IDLE:
                    roof.do_movement(direction)
                else:
                    roof.end_movement()
