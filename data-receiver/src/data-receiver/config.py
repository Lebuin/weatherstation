from datetime import timedelta

STATION_ID = 'biotope-serre'
STATION_KEY = 'biotope9000'


MQTT_HOST = 'mosquitto'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'data-receiver'
MQTT_USERNAME = 'data-receiver'
MQTT_PASSWORD = '7RPV2vWfD2rJgS9u'
MQTT_TOPIC_PREFIX = 'weatherstation'
MQTT_TOPIC = 'report'


RAIN_EVENT_DURATION = timedelta(hours=1)
