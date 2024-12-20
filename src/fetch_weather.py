import logging

import requests

from api_keys import ENDPOINTS


def fetch_weather_openweathermap(city, api_key):
    """Fetch weather data from OpenWeatherMap API."""
    try:
        url = f"{ENDPOINTS['OpenWeatherMap']}?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"OpenWeatherMap API error for {city}: {e}")
        return None

def fetch_weather_visualcrossing(city, api_key):
    """Fetch weather data from Visual Crossing API."""
    try:
        url = f"{ENDPOINTS['VisualCrossing']}/{city}?unitGroup=metric&key={api_key}&include=current,fcst&elements=tempmax,tempmin,temp,humidity,aqi,sunrise,sunset"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Visual Crossing API error for {city}: {e}")
        return None

def fetch_weather_weatherapi(city, api_key):
    """Fetch weather data from WeatherAPI."""
    try:
        url = f"{ENDPOINTS['WeatherAPI']}?key={api_key}&q={city}&aqi=yes"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"WeatherAPI error for {city}: {e}")
        return None

# "Fetch me weather!"
#
#      woof!
#         \   __
#          o-''|\_____/)
#           \_/|_)     )
#              \  __  /
#              (_/ (_/