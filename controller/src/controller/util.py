import collections.abc
import enum
import json
from dataclasses import dataclass
from datetime import datetime


class Mode(enum.Enum):
    GPIO = enum.auto()
    KEYBOARD = enum.auto()
    MQTT = enum.auto()


class Orientation(enum.Enum):
    NORTH = enum.auto()
    SOUTH = enum.auto()


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

    @property
    def sign(self):
        if self == self.OPEN:
            return 1
        else:
            return -1


class MovementMetaclass(type):
    def __iter__(cls) -> collections.abc.Generator['Movement', None, None]:
        for orientation in Orientation:
            for direction in Direction:
                yield cls(orientation, direction)

@dataclass
class Movement(metaclass=MovementMetaclass):
    orientation: Orientation
    direction: Direction

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.orientation == other.orientation and self.direction == other.direction

    def __str__(self):
        return f'{self.orientation}:{self.direction}'


    @property
    def opposite(self):
        return Movement(self.orientation, self.direction.opposite)


@dataclass
class PositionStep:
    position: float
    min_temperature: float
    max_temperature: float


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return int(o.timestamp())
        elif isinstance(o, enum.Enum):
            return o.name
        else:
            return super().default(o)


def round_or_none(n: float | None, precision: int):
    if n is None:
        return None
    else:
        return round(n, precision)
