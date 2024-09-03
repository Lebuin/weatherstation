import dataclasses
import logging
from datetime import datetime, timedelta

import openmeteo_requests
from openmeteo_sdk.VariablesWithTime import VariablesWithTime

from . import config

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class WeatherForecast:
    timestamp: datetime
    temperature: float
    wind_gust: float
    rain_event: float
    solar_radiation: float


class WeatherForecastFetcher:
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': 51.052,
        'longitude': 3.743,
        'hourly': ['temperature_2m', 'wind_gusts_10m', 'precipitation', 'shortwave_radiation'],
        'timezone': 'Europe/Brussels',
        'forecast_days': 2,
    }

    forecasts: list[WeatherForecast] = []
    last_fetch: datetime | None = None


    def get_forecast(self):
        self._update_forecast()

        if (
            self.last_fetch is not None
            and datetime.now() - self.last_fetch < config.WEATHER_FORECAST_VALIDITY
        ):
            return self._interpolate(self.forecasts, datetime.now())
        else:
            return None


    def _update_forecast(self):
        if (
            self.last_fetch is not None
            and datetime.now() - self.last_fetch < .5 * config.WEATHER_FORECAST_VALIDITY
        ):
            return

        forecasts = self._fetch_forecast()
        if forecasts is not None:
            self.forecasts = forecasts
            self.last_fetch = datetime.now()


    def _fetch_forecast(self):
        logger.info('Fetch weather forecast')

        openmeteo = openmeteo_requests.Client()
        responses = openmeteo.weather_api(self.url, params=self.params)
        response = responses[0]
        hourly = response.Hourly()

        if hourly is None:
            return

        reports = self._parse_forecast(hourly)
        return reports


    def _parse_forecast(self, hourly: VariablesWithTime):
        reports: list[WeatherForecast] = []
        start = datetime.fromtimestamp(hourly.Time())
        end = datetime.fromtimestamp(hourly.TimeEnd())
        interval = timedelta(seconds=hourly.Interval())
        for i in range(int((end - start) / interval)):
            temperature = hourly.Variables(self.params['hourly'].index('temperature_2m')).Values(i)  # type: ignore
            wind_gust = hourly.Variables(self.params['hourly'].index('wind_gusts_10m')).Values(i)   # type: ignore
            precipitation = hourly.Variables(self.params['hourly'].index('precipitation')).Values(i)  # type: ignore
            shortwave_radiation = hourly.Variables(self.params['hourly'].index('shortwave_radiation')).Values(i)  # type: ignore

            wind_gust += config.WEATHER_FORECAST_WIND_MARGIN

            report = WeatherForecast(
                timestamp=start + i * interval,
                temperature=temperature,
                wind_gust=wind_gust,
                rain_event=precipitation,
                solar_radiation=shortwave_radiation,
            )
            reports.append(report)

        return reports


    def _interpolate(self, reports: list[WeatherForecast], timestamp: datetime):
        prev_report = next(report for report in reports[::-1] if report.timestamp <= timestamp)
        next_report = next(report for report in reports if report.timestamp > timestamp)

        prev_factor = 1 - (timestamp - prev_report.timestamp).total_seconds() / 3600
        next_factor = 1 - prev_factor

        report = WeatherForecast(
            timestamp=timestamp,
            temperature=prev_report.temperature * prev_factor + next_report.temperature * next_factor,
            wind_gust=max(prev_report.wind_gust, next_report.wind_gust),
            rain_event=next_report.rain_event,
            solar_radiation=prev_report.solar_radiation * prev_factor + next_report.solar_radiation * next_factor,
        )
        return report

