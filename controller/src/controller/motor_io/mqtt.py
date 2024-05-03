from __future__ import annotations

import logging
from dataclasses import dataclass

from controller.mqtt_client import MQTTClient

from .. import config as _config
from .. import util
from .base import MotorIO

logger = logging.getLogger()

__all__ = (
    'MQTTIO',
)


@dataclass
class MovementConfig:
    topic: str


class MQTTIO(MotorIO):
    MovementConfig = MovementConfig
    Config = dict[util.Movement, MovementConfig]

    config: Config
    mqtt_client: MQTTClient

    active_inputs: dict[util.Movement, bool]


    def __init__(self, config: Config):
        self.config = config
        self.mqtt_client = MQTTClient()

        self.active_inputs = {
            movement: False
            for movement in util.Movement
        }

        for movement_config in self.config.values():
            self.mqtt_client.subscribe(movement_config.topic, self._on_mqtt_message)


    def _on_mqtt_message(self, topic, payload):
        for movement, movement_config in self.config.items():
                if movement_config.topic == topic:
                    self.active_inputs[movement] = (payload != '0')


    def read(self, movement: util.Movement) -> bool:
        return self.active_inputs[movement]


    def write(self, movement: util.Movement, active: bool) -> None:
        # Do nothing
        pass

