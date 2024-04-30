import fields
from app import app
from flask import abort, request
from mqtt_client import MQTTClient

mqtt_client = MQTTClient(
    host=app.config['MQTT_HOST'],
    port=app.config['MQTT_PORT'],
    client_id=app.config['MQTT_CLIENT_ID'],
    username=app.config['MQTT_USERNAME'],
    password=app.config['MQTT_PASSWORD'],
    topic_prefix=app.config['MQTT_TOPIC_PREFIX'],
)


def authorize():
    if (
        request.args.get('ID', None) != app.config['STATION_ID']
        or request.args.get('PASSWORD', None) != app.config['STATION_KEY']
    ):
        abort(403)


report_fields = {
    'outdoor/temperature': fields.Temperature('tempf'),
    'outdoor/humidity': fields.Humidity('humidity'),
    'outdoor/dewpoint': fields.Temperature('dewptf'),
    'outdoor/wind_chill': fields.Temperature('windchillf'),
    'outdoor/wind_direction': fields.WindDirection('winddir'),
    'outdoor/wind_speed': fields.WindSpeed('windspeedmph'),
    'outdoor/wind_gust': fields.WindSpeed('windgustmph'),
    'outdoor/rain': fields.Rain('rainin'),
    'outdoor/rain_daily': fields.Rain('dailyrainin'),
    'outdoor/rain_weekly': fields.Rain('weeklyrainin'),
    'outdoor/rain_monthly': fields.Rain('monthlyrainin'),
    'outdoor/rain_yearly': fields.Rain('yearlyrainin'),
    'outdoor/rain_total': fields.Rain('totalrainin'),
    'outdoor/solar_radiation': fields.SolarRadiation('solarradiation'),
    'outdoor/uv': fields.UV('UV'),
    'indoor/temperature': fields.Temperature('indoortempf'),
    'indoor/humidity': fields.Humidity('indoorhumidity'),
    'indoor/pressure': fields.Pressure('baromin'),
    'battery': fields.Battery('lowbatt'),
}


def get_report(request):
    report = {}
    for key, field in report_fields.items():
        try:
            report[key] = field.get_value(request)
        except Exception as e:
            app.logger.exception(e)
    return report


def publish_report(report):
    for key, value in report.items():
        mqtt_client.publish(key, value, retain=True)


@app.route('/weatherstation/updateweatherstation.php', methods=['GET'])
def report():
    authorize()
    report = get_report(request)
    publish_report(report)
    app.logger.debug(report)

    return 'OK'


app.logger.debug('data-receiver server started')
