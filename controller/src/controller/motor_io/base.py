from __future__ import annotations

import abc
import logging

from .. import motor

logger = logging.getLogger(__name__)



class MotorIO(abc.ABC):
    def read(self, motor: motor.Motor) -> bool:
        return self._do_read(motor)


    @abc.abstractmethod
    def _do_read(self, motor: motor.Motor) -> bool:
        return NotImplemented


    def write(self, motor: motor.Motor, value: bool) -> None:
        action = 'start' if value else 'stop'
        logger.info(f'{motor.orientation}:{motor.direction}: {action}')
        return self._do_write(motor, value)


    @abc.abstractmethod
    def _do_write(self, motor: motor.Motor, value: bool) -> None:
        return NotImplemented
