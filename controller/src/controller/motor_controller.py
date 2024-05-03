import enum
import logging
from dataclasses import dataclass
from datetime import datetime

from . import config
from . import motor_io as _motor_io
from . import util

logger = logging.getLogger(__name__)


@dataclass
class Action:
    movement: util.Movement
    fraction: float
    start: datetime | None = None

    @property
    def orientation(self):
        return self.movement.orientation

    @property
    def direction(self):
        return self.movement.direction

    @property
    def duration(self):
        return self.fraction * config.ROOF_MOVEMENT_DURATION


class MotorState(enum.Enum):
    INACTIVE = enum.auto()
    SCHEDULED = enum.auto()
    ONGOING = enum.auto()


class MotorController:
    motor_io: _motor_io.MotorIO
    current_action: Action | None = None
    next_action: Action | None = None


    def __init__(self):
        self.motor_io = _motor_io.create(config.MODE)


    def read(self, movement: util.Movement) -> bool:
        return self.motor_io.read(movement)

    def write(self, movement: util.Movement, active: bool) -> None:
        if active:
            logger.info(f'Start motor: {movement}')
        else:
            logger.info(f'Stop motor: {movement}')
        return self.motor_io.write(movement, active)


    def do_action(self, movement: util.Movement, fraction: float=1) -> None:
        if self._can_replace_action(movement, self.current_action):
            self.current_action = Action(movement, fraction, datetime.now())
            logger.debug(f'Do action: {self.current_action}')
            self.write(self.current_action.movement, True)

        elif (
            self.current_action is not None
            and self.current_action.orientation != movement.orientation
            and self._can_replace_action(movement, self.next_action)
        ):
            self.next_action = Action(movement, fraction)
            logger.debug(f'Schedule action: {self.next_action}')


    def _can_replace_action(self, movement: util.Movement, action: Action | None):
        return (
            action is None
            or action.orientation == movement.orientation
            and action.direction != movement.direction
        )


    def end_action(self, orientation: util.Orientation) -> None:
        if self.current_action and self.current_action.orientation == orientation:
            self.write(self.current_action.movement, False)
            self.current_action = None

            if self.next_action:
                action = self.next_action
                self.next_action = None
                self.do_action(action.movement, action.fraction)

        elif self.next_action and self.next_action.orientation == orientation:
            self.next_action = None


    def get_motor_state(self, orientation: util.Orientation) -> MotorState:
        if self.current_action and self.current_action.orientation == orientation:
            return MotorState.ONGOING

        elif self.next_action and self.next_action.orientation == orientation:
            return MotorState.SCHEDULED

        else:
            return MotorState.INACTIVE


    def tick(self) -> None:
        if (
            self.current_action
            and (
                self.current_action.start is None
                or datetime.now() - self.current_action.start > self.current_action.duration
            )
        ):
            self.end_action(self.current_action.orientation)
