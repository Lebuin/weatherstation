import enum
import logging
from datetime import datetime, timedelta

import requests

from . import config, util
from .motor_controller import MotorController, MotorState
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
    input_handled: set[tuple[util.Orientation, util.Direction]]

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
        if self.emergency != Emergency.NONE:
            self.do_emergency_movements()
        else:
            self.do_manual_movements()
            self.do_auto_movements()

        self.send_healthcheck()


    def do_movement(self, direction: util.Direction, fraction: float=1):
        for orientation in util.Orientation:
            movement = util.Movement(orientation, direction)
            self.motor_controller.do_action(movement, fraction)

    def close_roofs(self):
        self.do_movement(util.Direction.CLOSE)


    def curfew_is_ongoing(self, last_event: datetime, curfew: timedelta):
        return datetime.now() - last_event < curfew


    def read_inputs(self) -> dict[util.Movement, bool]:
        inputs = {}

        for movement in util.Movement:
            inputs[movement] = self.motor_controller.read(movement)

        return inputs


    def update_emergency(self) -> Emergency:
        if self.weather_monitor.is_offline:
            emergency = Emergency.WEATHERSTATION_OFFLINE
        elif (
            self.weather_monitor.report
            and self.weather_monitor.report['outdoor_wind_gust'] > config.HIGH_WIND
        ):
            emergency = Emergency.HIGH_WIND
        else:
            emergency = Emergency.NONE

        if emergency != self.emergency:
            if emergency != Emergency.NONE:
                logger.info(f'We are in emergency {emergency}, keeping all roofs closed from now on')
            else:
                logger.info(f'Emergency {self.emergency} is over')
        self.emergency = emergency

        return self.emergency


    def do_emergency_movements(self):
        if self.emergency != Emergency.NONE:
            self.close_roofs()

        if self.emergency == Emergency.HIGH_WIND:
            self.last_high_wind = self.weather_monitor.last_report_time


    def do_auto_movements(self) -> None:
        if (
            self.curfew_is_ongoing(self.last_auto_movement, config.AUTO_MOVEMENT_CURFEW)
            or self.curfew_is_ongoing(self.last_input, config.MANUAL_MOVEMENT_CURFEW)
            or not self.weather_monitor.report
        ):
            return

        if self.weather_monitor.report['indoor_temperature'] > config.MAX_INDOOR_TEMPERATURE:
            self.do_auto_movement(util.Direction.OPEN)
        elif self.weather_monitor.report['indoor_temperature'] < config.MIN_INDOOR_TEMPERATURE:
            self.do_auto_movement(util.Direction.CLOSE)


    def do_auto_movement(self, direction: util.Direction) -> None:
        self.do_movement(direction, config.AUTO_MOVEMENT_FRACTION)
        self.last_auto_movement = datetime.now()


    def do_manual_movements(self) -> None:
        inputs = self.read_inputs()

        for movement in util.Movement:
            if not inputs[movement]:
                self.input_handled.discard(movement)

            elif movement not in self.input_handled:
                self.input_handled.add(movement)
                self.last_input = datetime.now()
                motor_state = self.motor_controller.get_motor_state(movement.orientation)

                if motor_state == MotorState.INACTIVE:
                    self.motor_controller.do_action(movement)
                else:
                    self.motor_controller.end_action(movement.orientation)


    def send_healthcheck(self) -> None:
        if datetime.now() - self.last_healthcheck < config.HEALTHCHECK_INTERVAL:
            return
        self.last_healthcheck = datetime.now()

        url = config.HEALTHCHECK_URL
        if self.emergency != Emergency.NONE:
            url += f'/{self.emergency.value}'

        requests.post(url)
        logger.debug(f'Sent healthcheck with status {self.emergency.value} ({self.emergency})')
