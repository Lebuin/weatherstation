import logging
import typing

import paho.mqtt.client
import paho.mqtt.enums

logger = logging.getLogger(__name__)


class MQTTException(Exception):
    pass


class MQTTClient:
    topic_prefix: str
    callbacks: dict[str, typing.List[typing.Callable]]
    client: paho.mqtt.client.Client

    def __init__(self, host, port, client_id, username, password, topic_prefix=''):
        self.topic_prefix = topic_prefix
        self.callbacks = {}

        self.client = paho.mqtt.client.Client(paho.mqtt.enums.CallbackAPIVersion.VERSION2, client_id)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message
        self.client.connect(host, port)
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

        for callback in callbacks:
            callback(topic, payload)


    def _prefix_topic(self, topic):
        if self.topic_prefix:
            return f'{self.topic_prefix}/{topic}'
        else:
            return topic

    def _strip_topic(self, topic):
        if self.topic_prefix:
            return topic[len(self.topic_prefix)+1:]
        else:
            return topic


    def publish(self, topic, *args, **kwargs):
        topic = self._prefix_topic(topic)
        self.client.publish(topic, *args, **kwargs)


    def subscribe(self, topic, callback):
        topic = f'{self.topic_prefix}/{topic}'
        is_new_topic = topic not in self.callbacks

        if is_new_topic:
            self.callbacks[topic] = []

        self.callbacks[topic].append(callback)

        if is_new_topic:
            self.client.subscribe(topic)


    def unsubscribe(self, topic, callback):
        topic = f'{self.topic_prefix}/{topic}'
