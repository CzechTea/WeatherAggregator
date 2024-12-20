import csv
import os

def load_api_keys():
    """Load API keys from a CSV file or prompt the user to enter them."""
    keys = {}
    file_path = "api.csv"
    print("In order to program to properly work, You need to have valid API keys for OpenWeatherMap, Visual Crossing, WeatherApi")
    if not os.path.exists(file_path):
        print("API keys file have not been found.")
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["API", "Key"])
            for api in ["Open Weather Map", "Visual Crossing", "Weather API"]:
                key = input(f"Enter your API key for {api}: ").strip()
                writer.writerow([api, key])

    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            keys[row["API"]] = row["Key"]

    return keys

API_KEYS = load_api_keys()

ENDPOINTS = {
    "OpenWeatherMap": "http://api.openweathermap.org/data/2.5/weather",
    "VisualCrossing": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline",
    "WeatherAPI": "http://api.weatherapi.com/v1/current.json",
}
