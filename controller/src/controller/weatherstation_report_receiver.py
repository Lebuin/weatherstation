import dataclasses
import json
from datetime import datetime

from . import config
from .mqtt_client import MQTTClient


@dataclasses.dataclass
class WeatherstationReport:
    timestamp: datetime
    indoor_temperature: float | None  # ˚C
    outdoor_temperature: float | None  # ˚C
    outdoor_wind_gust: float | None  # km/h
    outdoor_rain_event: float | None  # mm in the past hour
    outdoor_solar_radiation: float | None  # W/m²


class WeatherstationReportReceiver:
    mqtt_client: MQTTClient
    report: WeatherstationReport | None = None
    startup_time: datetime = datetime.now()

    def __init__(self):
        self.mqtt_client = MQTTClient()
        self.mqtt_client.subscribe(config.MQTT_TOPIC_REPORT, self._on_mqtt_message)


    def get_report(self):
        if self.report and datetime.now() - self.report.timestamp < config.WEATHER_REPORT_VALIDITY:
            return self.report
        else:
            return None


    def _on_mqtt_message(self, topic: str, data: str):

        message = json.loads(data)
        report = WeatherstationReport(
            timestamp=datetime.fromisoformat(message['timestamp']),
            indoor_temperature=message.get('indoor_temperature'),
            outdoor_temperature=message.get('outdoor_temperature'),
            outdoor_wind_gust=message.get('outdoor_wind_gust'),
            outdoor_rain_event=message.get('outdoor_rain_event'),
            outdoor_solar_radiation=message.get('outdoor_solar_radiation'),
        )
        self.report = report
