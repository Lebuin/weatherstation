import json
from datetime import datetime

import fields
import paho.mqtt.publish as publish
from app import app
from flask import abort, request

from . import config

past_reports = []


def authorize():
    if (
        request.args.get('ID', None) != app.config['STATION_ID']
        or request.args.get('PASSWORD', None) != app.config['STATION_KEY']
    ):
        abort(403)


report_fields = {
    'outdoor_temperature': fields.Temperature('tempf'),
    'outdoor_humidity': fields.Humidity('humidity'),
    'outdoor_dewpoint': fields.Temperature('dewptf'),
    'outdoor_wind_chill': fields.Temperature('windchillf'),
    'outdoor_wind_direction': fields.WindDirection('winddir'),
    'outdoor_wind_speed': fields.WindSpeed('windspeedmph'),
    'outdoor_wind_gust': fields.WindSpeed('windgustmph'),
    'outdoor_rain': fields.Rain('rainin'),
    'outdoor_rain_daily': fields.Rain('dailyrainin'),
    'outdoor_rain_weekly': fields.Rain('weeklyrainin'),
    'outdoor_rain_monthly': fields.Rain('monthlyrainin'),
    'outdoor_rain_yearly': fields.Rain('yearlyrainin'),
    'outdoor_rain_total': fields.Rain('totalrainin'),
    'outdoor_solar_radiation': fields.SolarRadiation('solarradiation'),
    'outdoor_uv': fields.UV('UV'),
    'indoor_temperature': fields.Temperature('indoortempf'),
    'indoor_humidity': fields.Humidity('indoorhumidity'),
    'indoor_pressure': fields.Pressure('baromin'),
    'battery': fields.Battery('lowbatt'),
}


def get_report(request):
    report = {}
    for key, field in report_fields.items():
        try:
            report[key] = field.get_value(request)
        except Exception as e:
            app.logger.exception(e)

    now = datetime.now()
    report['timestamp'] = now.isoformat()
    past_reports.insert(0, report)

    while now - datetime.fromisoformat(past_reports[-1]['timestamp']) > config.RAIN_EVENT_DURATION:
        past_reports.pop()

    rain_total = report.get('outdoor_rain_total', None)
    past_rain_total = past_reports[-1].get('outdoor_rain_total', None)
    if rain_total is not None and past_rain_total is not None:
        report['outdoor_rain_event'] = rain_total - past_rain_total

    return report


def publish_report(report):
    payload = json.dumps(report)
    topic = app.config['MQTT_TOPIC']
    if app.config['MQTT_TOPIC_PREFIX']:
        topic = app.config['MQTT_TOPIC_PREFIX'] +'/' + topic

    publish.single(
        topic,
        payload,
        hostname=app.config['MQTT_HOST'],
        port=app.config['MQTT_PORT'],
        client_id=app.config['MQTT_CLIENT_ID'],
        auth={
            'username': app.config['MQTT_USERNAME'],
            'password': app.config['MQTT_PASSWORD'],
        },
    )


@app.route('/report', methods=['GET'])
def report():
    authorize()
    report = get_report(request)
    app.logger.debug(f'Publishing report: {report}')
    publish_report(report)

    return 'OK'


app.logger.debug('data-receiver server started')
