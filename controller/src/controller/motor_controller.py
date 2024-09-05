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
    start: datetime

    @property
    def orientation(self):
        return self.movement.orientation

    @property
    def direction(self):
        return self.movement.direction



class MotorController:
    last_stable_position: dict[util.Orientation, float]
    target_position: dict[util.Orientation, float]
    last_verification: dict[util.Orientation, datetime]
    current_action: Action | None

    def __init__(self):
        self.motor_io = _motor_io.create(config.MODE)

        self.last_stable_position = {
            util.Orientation.NORTH: 0,
            util.Orientation.SOUTH: 0,
        }
        self.target_position = {
            util.Orientation.NORTH: 0,
            util.Orientation.SOUTH: 0,
        }
        if config.ROOF_VERIFICATION_ON_STARTUP:
            self.last_verification = {
                util.Orientation.NORTH: datetime(1, 1, 1),
                util.Orientation.SOUTH: datetime(1, 1, 1),
            }
        else:
            self.last_verification = {
                util.Orientation.NORTH: datetime.now(),
                util.Orientation.SOUTH: datetime.now(),
            }
        self.current_action = None

        logger.info('MotorController is being initialized, stopping all roof movement')
        for orientation in util.Orientation:
            for direction in util.Direction:
                self.write(util.Movement(orientation, direction), False)


    def __del__(self):
        logger.info('MotorController is being deleted, closing all roofs')
        self.current_action = None
        for orientation in util.Orientation:
            self.write(util.Movement(orientation, util.Direction.CLOSE), True)


    def read(self, movement: util.Movement) -> bool:
        return self.motor_io.read(movement)

    def write(self, movement: util.Movement, active: bool) -> None:
        if active:
            self.write(movement.opposite, False)

        if active:
            logger.info(f'Start motor {movement}')
        else:
            logger.info(f'Stop motor {movement}')

        self.motor_io.write(movement, active)


    def _get_movement_duration(self, current_position, target_position):
        return abs(target_position - current_position) * config.ROOF_MOVEMENT_DURATION.total_seconds()


    @property
    def current_position(self) -> dict[util.Orientation, float]:
        current_position = {}

        for orientation in util.Orientation:
            position = self.last_stable_position[orientation]
            if self.current_action and self.current_action.orientation == orientation:
                duration = datetime.now() - self.current_action.start
                distance = duration / config.ROOF_MOVEMENT_DURATION
                position += self.current_action.direction.sign * distance
            current_position[orientation] = position

        return current_position


    def tick(self):
        self._check_end_current_action()
        self._check_start_verification()
        self._check_start_regular_action()


    def set_target_position(self, orientation: util.Orientation, position: float):
        logger.info(f'Set target position of roof {orientation} to {position:.2f}')
        self.target_position[orientation] = position

    def set_all_target_positions(self, position: float):
        for orientation in util.Orientation:
            self.set_target_position(orientation, position)


    def verify_position(self, orientation: util.Orientation):
        if (
            self.current_position[orientation] == 0
            and self.target_position[orientation] == 0
        ):
            logger.info(f'Verify roof {orientation} by closing')
            self.set_target_position(orientation, -1)

        elif (
            self.current_position[orientation] == 1
            and self.target_position[orientation] == 1
        ):
            logger.info(f'Verify roof {orientation} by opening')
            self.set_target_position(orientation, 2)


    def ensure_closed(self, orientation: util.Orientation):
        # We don't simply set target position 0: we want to be really sure that the roofs do a
        # full closing cycle, even if our estimate of their current position is wrong.
        self.set_target_position(orientation, self.current_position[orientation] - 1)

    def ensure_all_closed(self):
        for orientation in util.Orientation:
            self.ensure_closed(orientation)


    def _check_end_current_action(self):
        if not self.current_action:
            return

        orientation = self.current_action.orientation
        last_stable_position = self.last_stable_position[orientation]
        current_position = self.current_position[orientation]
        target_position = self.target_position[orientation]
        is_verification = abs(target_position - last_stable_position) >= 1
        # If the target position is fully closed: let the roof run a few extra seconds. We want
        # a tight fit when closing the roof, which isn't guaranteed after e.g. opening the roof
        # for 20 seconds, and then closing it for 20 seconds.
        if target_position <= 0:
            target_position -= .02

        if (current_position - target_position) * self.current_action.direction.sign >= 0:
            logger.info(f'Roof {orientation} has reached target position {target_position:.2f}')
            self._end_action()
            # If the target position was set out of bounds (e.g. for a verification), we need to
            # fix that here, otherwise the roof will keep on going forever.
            self.target_position[orientation] = min(max(target_position, 0), 1)

            if is_verification:
                self.last_verification[orientation] = datetime.now()


    def _check_start_verification(self):
        for orientation in util.Orientation:
            if self.current_action:
                return

            needs_verification = (
                datetime.now() - self.last_verification[orientation]
                > config.ROOF_VERIFICATION_INTERVAL
            )

            if needs_verification:
                self.verify_position(orientation)


    def _check_start_regular_action(self):
        for orientation in util.Orientation:
            if self.current_action:
                return

            current_position = self.current_position[orientation]
            target_position = self.target_position[orientation]

            if abs(target_position - current_position) < .001:
                continue

            if target_position > current_position:
                direction = util.Direction.OPEN
                direction_text = 'Open'
            else:
                direction = util.Direction.CLOSE
                direction_text = 'Close'

            duration = self._get_movement_duration(current_position, target_position)
            logger.info(
                f'{direction_text} roof {orientation} '
                f'from {current_position:.2f} to {target_position:.2f} '
                f'({duration:.0f}s)'
            )
            movement = util.Movement(orientation, direction)
            self._start_action(movement)



    def _start_action(self, movement):
        if self.current_action:
            raise Exception(f'Tried to start an action, but {self.current_action} is ongoing')

        self.current_action = Action(movement, datetime.now())
        self.write(movement, True)


    def _end_action(self):
        if not self.current_action:
            return

        orientation = self.current_action.orientation
        self.last_stable_position[orientation] = min(max(self.current_position[orientation], 0), 1)
        self.write(self.current_action.movement, False)
        self.current_action = None
