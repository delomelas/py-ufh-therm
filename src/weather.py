import shelve
from datetime import datetime

import openmeteo_requests
import requests_cache
from retry_requests import retry



class Weather:
    DBNAME = "weather"

    forecast = {}

    status = True

    def __init__(self):
        # load saved weather data from the shelf

        with shelve.open(self.DBNAME) as db:
            dkeys = db.keys()
            for k in dkeys:
                # discard anything older than now - we don't care about historical weather
                key = int(k)
                self.forecast[key] = db[k]

    def GetStatus(self):
        return self.status

    def FetchOpenMeteoWeather(self):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 51.3495,
            "longitude": -0.2494,
            "hourly": "temperature_2m",
            "timezone": "GMT",
            "forecast_days": 3,
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_time = range(hourly.Time(), hourly.TimeEnd(), hourly.Interval())

        weather = {}

        for t, temp in zip(hourly_time, hourly_temperature_2m):
            weather[t] = temp

        return weather

    def UpdateWeather(self):
        self.status = True

        # get 24h hourly forcast from an API

        try:
            weather = self.FetchOpenMeteoWeather()

            # if we were successful, update our internal db and shelf with the latest forecast
            with shelve.open(self.DBNAME) as db:
                for k in weather:
                    db[str(k)] = weather[k]
                    self.forecast[k] = weather[k]

        except Exception as e:
            print("Error refreshing weather data")
            print(e)
            self.status = False

    # returns a temperature for a given epoch time
    def GetTempForecast(self, t):

        if len(self.forecast) == 0:
            return 0

        # round the time to the nearest whole hour, as that's more likely to be in the db
        dt = datetime.fromtimestamp(t)
        dt = dt.replace(microsecond=0, second=0, minute=0)
        t = dt.timestamp()

        if t in self.forecast:
            return self.forecast[t]

        # return the temp that's within an hour of the forecast
        for dbtime in self.forecast:
            if t <= dbtime <= t + 3601:
                return self.forecast[dbtime]

        # if we've gone past the end of the list, return 0, we've no good weather forecast
        self.status = False
        return 0
