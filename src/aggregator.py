from concurrent.futures import ThreadPoolExecutor, as_completed

from fetch_weather import fetch_weather_visualcrossing, fetch_weather_openweathermap, fetch_weather_weatherapi


def aggregate_weather_data(city, data_sources):
    """Agregated data from the Weather APIs"""
    aggregated_data = {
        "city": city,
        "current_temp": [],
        "high_temp": [],
        "low_temp": [],
        "humidity": [],
        "aqi": [],
        "sunrise": None,
        "sunset": None
    }
    """It start 3 thread at the same time, they try to get weather data."""
    with ThreadPoolExecutor() as executor:
        futures = []
        for source, api_key in data_sources.items():
            if source == "OpenWeatherMap":
                futures.append(executor.submit(fetch_weather_openweathermap, city, api_key))
            elif source == "VisualCrossing":
                futures.append(executor.submit(fetch_weather_visualcrossing, city, api_key))
            elif source == "WeatherAPI":
                futures.append(executor.submit(fetch_weather_weatherapi, city, api_key))

        for future in as_completed(futures):
            data = future.result()
            if data:
                """As Weather APIs have different formats, we need to find them by their name"""
                if "main" in data:  # OpenWeatherMap format
                    aggregated_data["current_temp"].append(round(data["main"]["temp"]))
                    aggregated_data["high_temp"].append(round(data["main"]["temp_max"]))
                    aggregated_data["low_temp"].append(round(data["main"]["temp_min"]))
                    aggregated_data["humidity"].append(round(data["main"]["humidity"]))
                elif "currentConditions" in data:  # Visual Crossing format
                    current = data["currentConditions"]
                    aggregated_data["current_temp"].append(round(current.get("temp")))
                    aggregated_data["aqi"].append(current.get("aqi", "N/A"))
                    aggregated_data["sunrise"] = current.get("sunrise")
                    aggregated_data["sunset"] = current.get("sunset")
                elif "current" in data:  # WeatherAPI format
                    current = data["current"]
                    aggregated_data["current_temp"].append(round(current["temp_c"]))
                    aggregated_data["high_temp"].append(round(current["temp_c"]))
                    aggregated_data["low_temp"].append(round(current["temp_c"]))
                    aggregated_data["humidity"].append(round(current["humidity"]))

    """Aggregating data."""
    if aggregated_data["current_temp"]:
        aggregated_data["avg_current_temp"] = round(sum(aggregated_data["current_temp"]) / len(aggregated_data["current_temp"]))
    if aggregated_data["high_temp"]:
        aggregated_data["avg_high_temp"] = round(sum(aggregated_data["high_temp"]) / len(aggregated_data["high_temp"]))
    if aggregated_data["low_temp"]:
        aggregated_data["avg_low_temp"] = round(sum(aggregated_data["low_temp"]) / len(aggregated_data["low_temp"]))
    if aggregated_data["humidity"]:
        aggregated_data["avg_humidity"] = round(sum(aggregated_data["humidity"]) / len(aggregated_data["humidity"]))

    return aggregated_data
