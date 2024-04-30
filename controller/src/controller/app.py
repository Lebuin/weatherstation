from __future__ import annotations

import logging
import signal
import sys

from . import config, motor
from . import motor_io as _motor_io
from . import roof as _roof
from .graceful_killer import GracefulKiller
from .scheduler import scheduler


def signal_handler(signum, frame):
    print('Received signal')

signal.signal(signal.SIGTERM, signal_handler)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

killer = GracefulKiller()

motor_io = _motor_io.create(config.MODE)
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
    if killer.kill_now:
        for roof in roofs.values():
            roof.end_movement()
        return

    scheduler.delay(loop, config.POLL_DURATION)

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
