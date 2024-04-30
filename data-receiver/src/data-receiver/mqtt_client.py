from app import app
from paho.mqtt import client as mqtt_client


class MQTTClient:
    def __init__(self, host, port, client_id, username, password, topic_prefix):
        self.topic_prefix = topic_prefix

        self.client = mqtt_client.Client(client_id)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.connect(host, port)
        self.client.loop_start()


    def __del__(self):
        self.client.loop_stop()


    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            app.logger.exception(f'Failed to connect, return code {rc}')


    def publish(self, topic, payload):
        topic = f'{self.topic_prefix}/{topic}'
        self.client.publish(topic, payload, retain=True)
