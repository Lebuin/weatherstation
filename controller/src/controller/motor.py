from __future__ import annotations

import enum
import typing

from . import roof as _roof

if typing.TYPE_CHECKING:
    from . import motor_io as _motor_io


class Motor:
    class Direction(enum.Enum):
        OPEN = enum.auto()
        CLOSE = enum.auto()

        @property
        def opposite(self):
            if self == self.OPEN:
                return self.CLOSE
            elif self == self.CLOSE:
                return self.OPEN
            else:
                raise ValueError


    motor_io: _motor_io.MotorIO
    roof: _roof.Roof
    direction: Direction
    value: bool = False


    def __init__(self, motor_io: _motor_io.MotorIO, roof: _roof.Roof, direction: Direction):
        self.motor_io = motor_io
        self.roof = roof
        self.direction = direction
        self.write(False, force=True)


    @property
    def orientation(self) -> _roof.Roof.Orientation:
        return self.roof.orientation


    def read(self) -> bool:
        return self.motor_io.read(self)


    def write(self, value: bool, force=False) -> None:
        if value != self.value or force is True:
            self.value = value
            self.motor_io.write(self, value)
