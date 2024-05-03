import logging
import typing

import paho.mqtt.client
import paho.mqtt.enums

from . import config, util

logger = logging.getLogger(__name__)

__all__ = (
    'mqtt_client',
)


class MQTTException(Exception):
    pass


class MQTTClient(metaclass=util.Singleton):
    topic_prefix: str
    callbacks: dict[str, typing.List[typing.Callable[[str, str], None]]]
    client: paho.mqtt.client.Client

    def __init__(self):
        self.topic_prefix = config.MQTT_TOPIC_PREFIX
        self.callbacks = {}

        self.client = paho.mqtt.client.Client(
            paho.mqtt.enums.CallbackAPIVersion.VERSION2,
            config.MQTT_CLIENT_ID
        )
        self.client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT)
        self.client.loop_start()


    def __del__(self):
        self.client.loop_stop()


    def _on_connect(self, client: paho.mqtt.client.Client, userdata, flags, rc, properties):
        if rc != 0:
            raise MQTTException(f'Failed to connect to MQTT, return code {rc}')


    def _on_subscribe(self, client: paho.mqtt.client.Client, userdata, mid, rcs, properties):
        for rc in rcs:
            if rc.is_failure:
                raise MQTTException(f'Failed to subscribe: {rc}')


    def _on_unsubscribe(self, client: paho.mqtt.client.Client, userdata, mid, rcs, properties):
        for rc in rcs:
            if rc.is_failure:
                raise MQTTException(f'Failed to subscribe: {rc}')


    def _on_message(
        self,
        client: paho.mqtt.client.Client,
        userdata,
        message: paho.mqtt.client.MQTTMessage,
    ):
        topic = self._strip_topic(message.topic)
        payload = message.payload.decode()
        callbacks = self.callbacks.get(message.topic, [])

        logger.debug(f'Got message on {message.topic}: {payload}')

        for callback in callbacks:
            callback(topic, payload)


    def _prefix_topic(self, topic: str):
        if self.topic_prefix:
            return f'{self.topic_prefix}/{topic}'
        else:
            return topic

    def _strip_topic(self, topic: str):
        if self.topic_prefix:
            return topic[len(self.topic_prefix)+1:]
        else:
            return topic


    def publish(self, topic: str, *args, **kwargs):
        topic = self._prefix_topic(topic)
        self.client.publish(topic, *args, **kwargs)


    def subscribe(self, topic: str, callback: typing.Callable[[str, str], None]):
        topic = f'{self.topic_prefix}/{topic}'
        is_new_topic = topic not in self.callbacks

        if is_new_topic:
            self.callbacks[topic] = []

        self.callbacks[topic].append(callback)

        if is_new_topic:
            logger.debug(f'Subscribed to {topic}')
            self.client.subscribe(topic)


    def unsubscribe(self, topic, callback):
        topic = f'{self.topic_prefix}/{topic}'

        if topic not in self.callbacks:
            return

        try:
            self.callbacks[topic].remove(callback)
        except ValueError:
            pass

        if len(self.callbacks[topic]) == 0:
            del self.callbacks[topic]
            logger.debug(f'Unsubscribed from {topic}')
            self.client.unsubscribe(topic)
