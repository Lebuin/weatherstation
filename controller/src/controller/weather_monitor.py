import json
from datetime import datetime

from . import config
from .mqtt_client import MQTTClient


class WeatherMonitor:
    mqtt_client: MQTTClient
    report: dict | None = None
    last_report_time: datetime

    def __init__(self):
        self.last_report_time = datetime(1, 1, 1)
        self.mqtt_client = MQTTClient()
        self.mqtt_client.subscribe(config.MQTT_REPORT_TOPIC, self._on_mqtt_message)


    def _on_mqtt_message(self, topic: str, message: str):
        self.report = json.loads(message)
        self.last_report_time = datetime.now()


    @property
    def is_receiving(self) -> bool:
        return datetime.now() - self.last_report_time < config.WEATHER_REPORT_VALIDITY
