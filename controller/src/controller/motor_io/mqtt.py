from __future__ import annotations

import typing
from dataclasses import dataclass

from .. import motor as _motor
from .. import roof as _roof
from .base import MotorIO
from controller.mqtt_client import MQTTClient
from ..import config as _config

if typing.TYPE_CHECKING:
    import pynput

__all__ = (
    'MQTTIO',
)


@dataclass
class MotorConfig:
    topic: str


class MQTTIO(MotorIO):
    MotorConfig = MotorConfig
    Config = dict[_roof.Roof.Orientation, dict[_motor.Motor.Direction, MotorConfig]]

    config: Config
    mqtt_client: MQTTClient

    active_inputs: dict[_roof.Roof.Orientation, dict[_motor.Motor.Direction, bool]]


    def __init__(self, config: Config):
        self.config = config
        self.mqtt_client = MQTTClient(
            host=_config.MQTT_HOST,
            port=_config.MQTT_PORT,
            client_id=_config.MQTT_CLIENT_ID,
            username=_config.MQTT_USERNAME,
            password=_config.MQTT_PASSWORD,
            topic_prefix=_config.MQTT_TOPIC_PREFIX
        )

        self.active_inputs = {
            _roof.Roof.Orientation.NORTH: {
                _motor.Motor.Direction.OPEN: False,
                _motor.Motor.Direction.CLOSE: False,
            },
            _roof.Roof.Orientation.SOUTH: {
                _motor.Motor.Direction.OPEN: False,
                _motor.Motor.Direction.CLOSE: False,
            },
        }

        for roof_configs in config.values():
            for motor_config in roof_configs.values():
                self.mqtt_client.subscribe(motor_config.topic, self._on_mqtt_message)


    def _on_mqtt_message(self, topic, payload):
        for orientation in self.config.keys():
            for direction, motor_config in self.config[orientation].items():
                if motor_config.topic == topic:
                    self.active_inputs[orientation][direction] = (payload != '0')


    def _do_read(self, motor: _motor.Motor) -> bool:
        return self.active_inputs[motor.orientation][motor.direction]


    def _do_write(self, motor: _motor.Motor, active: bool) -> None:
        # Do nothing
        pass

