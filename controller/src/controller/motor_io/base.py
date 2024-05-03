from __future__ import annotations

import abc
import logging

from .. import util

logger = logging.getLogger(__name__)



class MotorIO(abc.ABC):
    @abc.abstractmethod
    def read(self, movement: util.Movement) -> bool:
        return NotImplemented


    @abc.abstractmethod
    def write(self, movement: util.Movement, active: bool) -> None:
        return NotImplemented
