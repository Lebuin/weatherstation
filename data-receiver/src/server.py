from flask import Flask, request, abort
from . import fields


app = Flask(__name__)
app.config.from_object('src.config')


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


@app.route('/report', methods=['GET'])
def hello_world():
    authorize()
    app.logger.debug(request.args)

    values = {}
    for key, field in report_fields.items():
        try:
            values[key] = field.get_value(request)
        except Exception as e:
            app.logger.exception(e)

    app.logger.debug(values)

    return 'OK'
