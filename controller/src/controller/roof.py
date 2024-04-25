from __future__ import annotations

import enum
import typing

from . import config, motor
from .scheduler import scheduler

if typing.TYPE_CHECKING:
    from . import motor_io as _motor_io


class Roof:
    class Orientation(enum.Enum):
        NORTH = enum.auto()
        SOUTH = enum.auto()

    class State(enum.Enum):
        IDLE = enum.auto()
        OPENING = enum.auto()
        CLOSING = enum.auto()


    motor_io: _motor_io.MotorIO
    orientation: Orientation
    motors: dict[motor.Motor.Direction, motor.Motor]
    # Used to dismiss the end of an action if it has already been superseded by a new action
    action_counter = 0


    def __init__(self, motor_io: _motor_io.MotorIO, orientation: Orientation):
        self.motor_io = motor_io
        self.orientation = orientation
        self.motors = {
            motor.Motor.Direction.OPEN: motor.Motor(motor_io, self, motor.Motor.Direction.OPEN),
            motor.Motor.Direction.CLOSE: motor.Motor(motor_io, self, motor.Motor.Direction.CLOSE),
        }


    @property
    def state(self):
        if self.motors[motor.Motor.Direction.OPEN].state == motor.Motor.State.ACTIVE:
            return self.State.OPENING
        elif self.motors[motor.Motor.Direction.CLOSE].state == motor.Motor.State.ACTIVE:
            return self.State.CLOSING
        else:
            return self.State.IDLE


    def open(self, fraction: float=1) -> None:
        self.do_movement(motor.Motor.Direction.OPEN, fraction)

    def close(self, fraction: float=1) -> None:
        self.do_movement(motor.Motor.Direction.CLOSE, fraction)


    def do_movement(self, direction: motor.Motor.Direction, fraction: float=1) -> None:
        self.action_counter += 1

        self.write_to_motor(direction.opposite, False)
        self.write_to_motor(direction, True)

        delay = fraction * config.roof_movement_duration
        scheduler.delay(self._end_movement_after_timeout, delay, self.action_counter)


    def end_movement(self) -> None:
        self.write_to_motor(motor.Motor.Direction.OPEN, False)
        self.write_to_motor(motor.Motor.Direction.CLOSE, False)


    def _end_movement_after_timeout(self, action_counter: int) -> None:
        if action_counter == self.action_counter:
            self.end_movement()


    def write_to_motor(self, direction: motor.Motor.Direction, value: bool) -> None:
        motor = self.motors[direction]
        motor.write(value)
