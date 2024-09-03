import enum
import logging
from datetime import datetime

from .weather_forecast_fetcher import WeatherForecast, WeatherForecastFetcher
from .weatherstation_report_receiver import (WeatherstationReport,
                                             WeatherstationReportReceiver)

logger = logging.getLogger(__name__)


DEFAULT_TIMESTAMP = datetime(1, 1, 1)

class Datasource(enum.Enum):
    WEATHERSTATION = enum.auto()
    FORECAST = enum.auto()
    NONE = enum.auto()


class WeatherReport:
    timestamp: datetime = DEFAULT_TIMESTAMP

    indoor_data_source: Datasource = Datasource.NONE
    indoor_temperature: float | None = None

    outdoor_data_source: Datasource = Datasource.NONE
    outdoor_temperature: float | None = None
    outdoor_wind_gust: float | None = None
    outdoor_rain_event: float | None = None
    outdoor_solar_radiation: float | None = None

    def import_station_report(self, station_report: WeatherstationReport):
        if self.timestamp == DEFAULT_TIMESTAMP:
            self.timestamp = station_report.timestamp

        if station_report.indoor_temperature:
            self.indoor_data_source = Datasource.WEATHERSTATION
            self.indoor_temperature = station_report.indoor_temperature

        if station_report.outdoor_temperature is not None:
            self.outdoor_data_source = Datasource.WEATHERSTATION
            self.outdoor_temperature = station_report.outdoor_temperature
            self.outdoor_wind_gust = station_report.outdoor_wind_gust
            self.outdoor_rain_event = station_report.outdoor_rain_event
            self.outdoor_solar_radiation = station_report.outdoor_solar_radiation


    def import_forecast(self, forecast: WeatherForecast):
        if self.timestamp == DEFAULT_TIMESTAMP:
            self.timestamp = forecast.timestamp

        self.outdoor_data_source = Datasource.FORECAST
        self.outdoor_temperature = forecast.temperature
        self.outdoor_wind_gust = forecast.wind_gust
        self.outdoor_rain_event = forecast.rain_event
        self.outdoor_solar_radiation = forecast.solar_radiation



class WeatherMonitor:
    station_report_receiver: WeatherstationReportReceiver
    forecast_fetcher: WeatherForecastFetcher

    def __init__(self):
        self.station_report_receiver = WeatherstationReportReceiver()
        self.forecast_fetcher = WeatherForecastFetcher()


    def get_report(self):
        report = WeatherReport()

        station_report = self.station_report_receiver.get_report()
        if station_report:
            report.import_station_report(station_report)

        if report.outdoor_data_source is Datasource.NONE:
            forecast = self.forecast_fetcher.get_forecast()
            if forecast:
                report.import_forecast(forecast)

        return report
