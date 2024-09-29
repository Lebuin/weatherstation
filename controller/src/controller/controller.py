import enum
import json
import logging
from datetime import datetime, timedelta

import requests

from . import config, util
from .motor_controller import MotorController
from .mqtt_client import MQTTClient
from .weather_monitor import Datasource, WeatherMonitor, WeatherReport

logger = logging.getLogger(__name__)


class Status(enum.Enum):
    OK = 0
    UNCAUGHT_EXCEPTION = 1
    HIGH_WIND = 43
    FORECAST_OFFLINE = 70
    WEATHERSTATION_OFFLINE = 30
    WEATHERSTATION_OUTDOOR_OFFLINE = 130


class Controller:
    weather_monitor: WeatherMonitor
    motor_controller: MotorController

    startup_time = datetime.now()
    status: Status = Status.OK
    # We only want each input press to be handled once, so we keep track of which ones we've
    # already handled.
    input_handled: set[util.Movement]

    last_manual_input: datetime = datetime.fromtimestamp(0)
    last_high_wind: datetime = datetime.fromtimestamp(0)
    last_healthcheck: datetime = datetime.now()

    last_state_published: datetime = datetime.fromtimestamp(0)


    def __init__(self):
        self.weather_monitor = WeatherMonitor()
        self.motor_controller = MotorController()
        self.input_handled = set()


    def tick(self):
        try:
            self.motor_controller.tick()

            report = self.weather_monitor.get_report()
            self.update_status(report)

            self.do_limit_movements(report)
            self.do_manual_movements(report)
            self.do_temperature_movements(report)

            self.publish_state(report)

            try:
                self.send_healthcheck()
            except Exception as e:
                logger.error(e)
        except Exception as e:
            self.send_healthcheck(Status.UNCAUGHT_EXCEPTION)
            raise e


    def get_max_roof_position(self, report: WeatherReport):
        if self.status in (Status.HIGH_WIND, Status.FORECAST_OFFLINE):
            return 0
        elif report.outdoor_rain_event is not None and report.outdoor_rain_event > config.RAIN_THRESHOLD:
            return config.RAIN_MAX_POSITION
        else:
            return 1


    def get_platformed_position(self, position: float, report: WeatherReport) -> float:
        min_position = 0
        max_position = self.get_max_roof_position(report)
        return min(max_position, max(min_position, position))


    def read_inputs(self) -> dict[util.Movement, bool]:
        inputs = {}

        for movement in util.Movement:
            inputs[movement] = self.motor_controller.read(movement)

        return inputs


    def get_indoor_temperature(self, report: WeatherReport):
        if report.indoor_temperature is not None:
            return report.indoor_temperature

        elif report.outdoor_temperature is not None and report.outdoor_solar_radiation is not None:
            outdoor_temperature = report.outdoor_temperature
            indoor_bonus = 2
            solar_bonus = report.outdoor_solar_radiation * .02
            indoor_temperature = outdoor_temperature + indoor_bonus + solar_bonus
            return indoor_temperature

        else:
            raise Exception('Can\'t calculate indoor temperature with missing outdoor report')


    def update_status(self, report: WeatherReport):
        if datetime.now() - self.startup_time < timedelta(minutes=2):
            return

        if report.outdoor_wind_gust is not None and report.outdoor_wind_gust > config.HIGH_WIND:
            self.last_high_wind = report.timestamp

        if datetime.now() - self.last_high_wind < config.HIGH_WIND_CURFEW:
            status = Status.HIGH_WIND
        elif report.outdoor_data_source is Datasource.NONE:
            status = Status.FORECAST_OFFLINE
        elif report.indoor_data_source is Datasource.NONE:
            status = Status.WEATHERSTATION_OFFLINE
        elif report.outdoor_data_source is not Datasource.WEATHERSTATION:
            status = Status.WEATHERSTATION_OUTDOOR_OFFLINE
        else:
            status = Status.OK

        if status != self.status:
            logger.info(f'Changed from status {self.status} to {status}')
            self.status = status


    def do_limit_movements(self, report: WeatherReport) -> None:
        """Ensure the roofs are not opened further than their maximum allowed position."""

        max_position = self.get_max_roof_position(report)
        for orientation in util.Orientation:
            if self.motor_controller.target_position[orientation] > max_position:
                if max_position == 0:
                    self.motor_controller.ensure_closed(orientation)
                elif max_position < 1:
                    self.motor_controller.set_target_position(orientation, max_position)


    def do_temperature_movements(self, report: WeatherReport) -> None:
        """Automatically open/close the roofs based on the indoor temperature."""

        if datetime.now() - self.last_manual_input < config.MANUAL_MOVEMENT_CURFEW:
            return

        if (
            report.indoor_data_source == Datasource.NONE
            and report.outdoor_data_source == Datasource.NONE
        ):
            return

        temperature = self.get_indoor_temperature(report)

        for orientation in util.Orientation:
            for i, step in enumerate(config.POSITION_STEPS[:-1]):
                step_position = self.get_platformed_position(step.position, report)
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
                step_position = self.get_platformed_position(step.position, report)
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


    def do_manual_movements(self, report: WeatherReport) -> None:
        """Move the roofs based on movements received through the manual buttons."""

        inputs = self.read_inputs()

        for movement in util.Movement:
            if not inputs[movement]:
                self.input_handled.discard(movement)

            elif movement not in self.input_handled:
                logger.info(f'Got manual input: {movement}')
                self.input_handled.add(movement)
                self.last_manual_input = datetime.now()

                orientation = movement.orientation
                direction = movement.direction
                current_position = self.motor_controller.current_position[orientation]
                target_position = self.motor_controller.target_position[orientation]
                movement_ongoing = (target_position != current_position)

                if movement_ongoing:
                    logger.info('Cancel ongoing movement')
                    target_position = self.get_platformed_position(current_position, report)

                elif direction == util.Direction.OPEN:
                    if current_position == 1:
                        # When someone presses the "open" button while we think the roof is
                        # already fully opened, it may be because in reality it's not fully opened.
                        self.motor_controller.verify_position(orientation)
                    else:
                        target_position = self.get_platformed_position(1, report)
                        self.motor_controller.set_target_position(orientation, target_position)

                elif direction == util.Direction.CLOSE:
                    if current_position == 0:
                        self.motor_controller.verify_position(orientation)
                    else:
                        target_position = self.get_platformed_position(0, report)
                        self.motor_controller.set_target_position(orientation, target_position)


    def publish_state(self, report: WeatherReport) -> None:
        if datetime.now() - self.last_state_published < config.STATE_PUBLISH_INTERVAL:
            return

        self.do_publish_state(report)
        self.last_state_published = datetime.now()


    def do_publish_state(self, report: WeatherReport) -> None:
        mqtt_client = MQTTClient()

        if report.indoor_data_source is None and report.outdoor_data_source is None:
            indoor_temperature = None
        else:
            indoor_temperature = self.get_indoor_temperature(report)

        message: dict = {
            'timestamp': datetime.now(),

            'status': {
                'status': self.status,

                'last_manual_input': util.datetime_or_none(self.last_manual_input),
                'last_high_wind': util.datetime_or_none(self.last_high_wind),
                'last_healthcheck': util.datetime_or_none(self.last_healthcheck),
            },

            'parameters': {
                'min_temperature': config.POSITION_STEPS[1].min_temperature,
                'max_temperature': config.POSITION_STEPS[-2].max_temperature,
                'high_wind': config.HIGH_WIND,
                'rain_threshold': config.RAIN_THRESHOLD,
            },

            'weather_report': {
                'timestamp': util.datetime_or_none(report.timestamp),

                'indoor': {
                    'data_source': report.indoor_data_source,
                    'temperature': util.round_or_none(indoor_temperature, 1),
                },

                'outdoor': {
                    'data_source': report.outdoor_data_source,
                    'temperature': util.round_or_none(report.outdoor_temperature, 1),
                    'wind_gust': util.round_or_none(report.outdoor_wind_gust, 1),
                    'rain_event': util.round_or_none(report.outdoor_rain_event, 1),
                    'solar_radiation': util.round_or_none(report.outdoor_solar_radiation, 0),
                }
            },


            'roofs': {},
        }

        for orientation in util.Orientation:
            message['roofs'][orientation.name.lower()] = {
                'position': round(max(0, min(1, self.motor_controller.current_position[orientation])), 2),
                'target': round(max(0, min(1, self.motor_controller.target_position[orientation])), 2),
                'last_verification': util.datetime_or_none(self.motor_controller.last_verification[orientation]),
            }

        data = json.dumps(message, cls=util.JSONEncoder)
        mqtt_client.publish(config.MQTT_TOPIC_STATE, data, retain=True)


    def send_healthcheck(self, status: Status | None=None) -> None:
        if status is None:
            status = self.status

        if not config.SEND_HEALTHCHECKS:
            return

        if datetime.now() - self.last_healthcheck < config.HEALTHCHECK_INTERVAL:
            return
        self.last_healthcheck = datetime.now()


        url = f'{config.HEALTHCHECK_URL}/{status.value}'
        requests.post(url)

        logger.debug(f'Sent healthcheck with status {status.value} ({status})')
