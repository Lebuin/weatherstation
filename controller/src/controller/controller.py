import dataclasses
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


@dataclasses.dataclass
class RainEvent:
    timestamp: datetime
    rain_total: float


class Controller:
    weather_monitor: WeatherMonitor
    motor_controller: MotorController

    emergency: Emergency = Emergency.NONE
    # We only want each input press to be handled once, so we keep track of which ones we've
    # already handled.
    input_handled: set[util.Movement]

    last_input: datetime = datetime(1, 1, 1)
    last_high_wind: datetime = datetime(1, 1, 1)
    last_healthcheck: datetime = datetime.now()
    # This list contains the rain totals for the past hour, with the first element being the most
    # recent event.
    rain_history: list[RainEvent] = []


    def __init__(self):
        self.weather_monitor = WeatherMonitor()
        self.motor_controller = MotorController()
        self.input_handled = set()


    def tick(self):
        self.motor_controller.tick()

        self.update_rain_history()

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


    def rain_curfew_is_ongoing(self):
        if len(self.rain_history) < 2:
            return False

        rain_fallen = self.rain_history[0].rain_total - self.rain_history[-1].rain_total
        duration = self.rain_history[0].timestamp - self.rain_history[-1].timestamp
        rain_rate = rain_fallen / duration.total_seconds() * 3600  # mm per hour
        rain_threshold = config.RAIN_THRESHOLD / config.RAIN_CURFEW.total_seconds() * 3600

        return rain_rate > rain_threshold


    def get_platformed_position(self, position: float) -> float:
        min_position = 0
        if self.rain_curfew_is_ongoing():
            max_position = config.RAIN_MAX_POSITION
        else:
            max_position = 1

        return min(max_position, max(min_position, position))


    def read_inputs(self) -> dict[util.Movement, bool]:
        inputs = {}

        for movement in util.Movement:
            inputs[movement] = self.motor_controller.read(movement)

        return inputs


    def update_rain_history(self):
        if not self.weather_monitor.report:
            return

        timestamp = self.weather_monitor.last_report_time
        if (
            len(self.rain_history) > 0
            and timestamp == self.rain_history[0].timestamp
        ):
            return

        rain_event = RainEvent(
            timestamp=timestamp,
            rain_total=self.weather_monitor.report['outdoor_rain_total']
        )
        self.rain_history.insert(0, rain_event)
        while self.rain_history[0].timestamp < timestamp - config.RAIN_CURFEW:
            self.rain_history.pop()


        if self.rain_curfew_is_ongoing():
            for orientation in util.Orientation:
                if self.motor_controller.target_position[orientation] > config.RAIN_MAX_POSITION:
                    logger.info(f'It has started raining, closing roof {orientation} to {config.RAIN_MAX_POSITION:.2f}')
                    self.motor_controller.set_target_position(orientation, config.RAIN_MAX_POSITION)


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
                step_position = self.get_platformed_position(step.position)
                if (
                    self.motor_controller.target_position[orientation] > step_position
                    and temperature < config.POSITION_STEPS[i + 1].min_temperature
                ):
                    logger.info(
                        f'Temperature {temperature} is too low for roof {orientation} at position '
                        f'{self.motor_controller.target_position[orientation]:.2f}, closing to '
                        f'{step_position:.2f}'
                    )
                    self.motor_controller.set_target_position(orientation, step_position)

            for i, step in reversed(list(enumerate(config.POSITION_STEPS))[1:]):
                step_position = self.get_platformed_position(step.position)
                if (
                    self.motor_controller.target_position[orientation] < step_position
                    and temperature > config.POSITION_STEPS[i - 1].max_temperature
                ):
                    logger.info(
                        f'Temperature {temperature} is too high for roof {orientation} at position '
                        f'{self.motor_controller.target_position[orientation]:.2f}, opening to '
                        f'{step_position:.2f}'
                    )
                    self.motor_controller.set_target_position(orientation, step_position)


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
                    target_position = self.get_platformed_position(current_position)

                elif direction == util.Direction.OPEN:
                    if current_position == 1:
                        # When someone presses the "open" button while we think the roof is
                        # already fully opened, it may be because in reality it's not fully opened.
                        # So we set the target position out of bounds to ensure fully opening the
                        # roof for real.
                        target_position = 2
                    else:
                        target_position = self.get_platformed_position(1)

                elif direction == util.Direction.CLOSE:
                    if current_position == 0:
                        target_position = -1
                    else:
                        target_position = self.get_platformed_position(0)

                self.motor_controller.set_target_position(orientation, target_position)


    def send_healthcheck(self) -> None:
        if not config.SEND_HEALTHCHECKS:
            return

        if datetime.now() - self.last_healthcheck < config.HEALTHCHECK_INTERVAL:
            return
        self.last_healthcheck = datetime.now()

        if self.emergency != Emergency.NONE:
            status = self.emergency.value
        else:
            status = 0
        url = f'{config.HEALTHCHECK_URL}/{status}'
        requests.post(url)

        logger.debug(f'Sent healthcheck with status {self.emergency.value} ({self.emergency})')
