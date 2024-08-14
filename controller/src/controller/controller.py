import enum
import logging
from datetime import datetime, timedelta

import requests

from . import config, util
from .motor_controller import MotorController
from .weather_monitor import WeatherMonitor

logger = logging.getLogger(__name__)


class Emergency(enum.Enum):
    NONE = 0
    HIGH_WIND = 43
    WEATHERSTATION_OFFLINE = 30


class Controller:
    weather_monitor: WeatherMonitor
    motor_controller: MotorController

    emergency: Emergency = Emergency.NONE
    # We only want each input press to be handled once, so we keep track of which ones we've
    # already sent.
    input_handled: set[util.Movement]

    last_input: datetime = datetime(1, 1, 1)
    last_auto_movement: datetime = datetime(1, 1, 1)
    last_high_wind: datetime = datetime(1, 1, 1)
    last_healthcheck: datetime = datetime.now()


    def __init__(self):
        self.weather_monitor = WeatherMonitor()
        self.motor_controller = MotorController()
        self.input_handled = set()


    def tick(self):
        self.motor_controller.tick()

        self.update_emergency()
        if self.emergency == Emergency.NONE:
            self.do_manual_movements()
            self.do_auto_movements()

        try:
            self.send_healthcheck()
        except Exception as e:
            logger.error(e)


    def curfew_is_ongoing(self, last_event: datetime, curfew: timedelta):
        return datetime.now() - last_event < curfew


    def read_inputs(self) -> dict[util.Movement, bool]:
        inputs = {}

        for movement in util.Movement:
            inputs[movement] = self.motor_controller.read(movement)

        return inputs


    def update_emergency(self):
        if (
            self.weather_monitor.report
            and self.weather_monitor.report['outdoor_wind_gust'] > config.HIGH_WIND
        ):
            self.last_high_wind = self.weather_monitor.last_report_time

        if self.weather_monitor.is_offline:
            emergency = Emergency.WEATHERSTATION_OFFLINE
        elif datetime.now() - self.last_high_wind < config.HIGH_WIND_CURFEW:
            emergency = Emergency.HIGH_WIND
        else:
            emergency = Emergency.NONE

        if emergency != self.emergency:
            if emergency != Emergency.NONE:
                logger.info(f'We are in emergency {emergency}, closing all roofs')
                self.motor_controller.ensure_closed()
            else:
                logger.info(f'Emergency {self.emergency} is over')
        self.emergency = emergency


    def do_auto_movements(self) -> None:
        if (
            self.curfew_is_ongoing(self.last_input, config.MANUAL_MOVEMENT_CURFEW)
            or not self.weather_monitor.report
        ):
            return

        temperature = self.weather_monitor.report['indoor_temperature']
        for orientation in util.Orientation:
            for i, step in enumerate(config.POSITION_STEPS[:-1]):
                if (
                    self.motor_controller.target_position[orientation] > step.position
                    and temperature < config.POSITION_STEPS[i + 1].min_temperature
                ):
                    logger.info(
                        f'Temperature {temperature} is too low for roof {orientation} at position '
                        f'{self.motor_controller.target_position[orientation]:.2f}, closing to '
                        f'{step.position:.2f}'
                    )
                    self.motor_controller.set_target_position(orientation, step.position)

            for i, step in reversed(list(enumerate(config.POSITION_STEPS))[1:]):
                if (
                    self.motor_controller.target_position[orientation] < step.position
                    and temperature > config.POSITION_STEPS[i - 1].max_temperature
                ):
                    logger.info(
                        f'Temperature {temperature} is too high for roof {orientation} at position '
                        f'{self.motor_controller.target_position[orientation]:.2f}, opening to '
                        f'{step.position:.2f}'
                    )
                    self.motor_controller.set_target_position(orientation, step.position)


    def set_auto_position(self, position: float) -> None:
        self.motor_controller.set_all_target_positions(position)
        self.last_auto_movement = datetime.now()


    def do_manual_movements(self) -> None:
        inputs = self.read_inputs()

        for movement in util.Movement:
            if not inputs[movement]:
                self.input_handled.discard(movement)

            elif movement not in self.input_handled:
                logger.info(f'Got manual input: {movement}')
                self.input_handled.add(movement)
                self.last_input = datetime.now()

                orientation = movement.orientation
                direction = movement.direction
                current_position = self.motor_controller.current_position[orientation]
                target_position = self.motor_controller.target_position[orientation]
                movement_ongoing = (target_position != current_position)

                if movement_ongoing:
                    logger.info('Cancel ongoing movement')
                    target_position = current_position

                elif direction == util.Direction.OPEN:
                    if current_position == 1:
                        # When someone presses the "open" button while we think the roof is
                        # already fully opened, it may be because in reality it's not fully opened.
                        # So we set the target position out of bounds to ensure fully opening the
                        # roof for real.
                        target_position = 2
                    else:
                        target_position = 1

                elif direction == util.Direction.CLOSE:
                    if current_position == 0:
                        target_position = -1
                    else:
                        target_position = 0

                self.motor_controller.set_target_position(orientation, target_position)


    def send_healthcheck(self) -> None:
        if datetime.now() - self.last_healthcheck < config.HEALTHCHECK_INTERVAL:
            return
        self.last_healthcheck = datetime.now()

        url = config.HEALTHCHECK_URL
        if self.emergency != Emergency.NONE:
            url += f'/{self.emergency.value}'

        if config.SEND_HEALTHCHECKS:
            requests.post(url)
        logger.debug(f'Sent healthcheck with status {self.emergency.value} ({self.emergency})')
