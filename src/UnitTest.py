import unittest
from unittest.mock import patch, MagicMock
from aggregator import aggregate_weather_data
from fetch_weather import (
    fetch_weather_openweathermap,
    fetch_weather_visualcrossing,
    fetch_weather_weatherapi,
)
from preferences import load_preferences, save_preferences
from api_keys import load_api_keys

class TestWeatherAggregator(unittest.TestCase):
    def setUp(self):
        self.city = "TestCity"
        self.data_sources = {
            "OpenWeatherMap": "test_openweathermap_key",
            "VisualCrossing": "test_visualcrossing_key",
            "WeatherAPI": "test_weatherapi_key",
        }

    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_aggregate_weather_data(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 50}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 21,
                "tempmax": 26,
                "tempmin": 16,
                "humidity": 55,
                "aqi": 42,
                "sunrise": "6:00 AM",
                "sunset": "8:00 PM",
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 22, "humidity": 60}
        }

        result = aggregate_weather_data(self.city, self.data_sources)

        self.assertEqual(result["avg_current_temp"], 21)
        self.assertEqual(result["avg_high_temp"], 26)
        self.assertEqual(result["avg_low_temp"], 16)
        self.assertEqual(result["avg_humidity"], 55)
        self.assertIn(42, result["aqi"])
        self.assertEqual(result["sunrise"], "6:00 AM")
        self.assertEqual(result["sunset"], "8:00 PM")

    @patch("fetch_weather.fetch_weather_openweathermap")
    def test_aggregate_weather_data_with_missing_source(self, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 50}
        }

        incomplete_sources = {
            "OpenWeatherMap": "test_openweathermap_key",
        }

        result = aggregate_weather_data(self.city, incomplete_sources)

        self.assertEqual(result["avg_current_temp"], 20)
        self.assertEqual(result["avg_high_temp"], 25)
        self.assertEqual(result["avg_low_temp"], 15)
        self.assertEqual(result["avg_humidity"], 50)

class TestPreferences(unittest.TestCase):
    def setUp(self):
        self.preferences_file = "test_preferences.txt"
        self.sample_preferences = ["CityA", "CityB"]
        with open(self.preferences_file, "w") as file:
            file.write("\n".join(self.sample_preferences))

    def tearDown(self):
        import os

        if os.path.exists(self.preferences_file):
            os.remove(self.preferences_file)

    @patch("preferences.PREFERENCES_FILE", new_callable=lambda: "test_preferences.txt")
    def test_load_preferences(self, mock_file):
        preferences = load_preferences()
        self.assertEqual(preferences, self.sample_preferences)

    @patch("preferences.PREFERENCES_FILE", new_callable=lambda: "test_preferences.txt")
    def test_save_preferences(self, mock_file):
        new_preferences = ["CityX", "CityY"]
        save_preferences(new_preferences)
        with open(self.preferences_file, "r") as file:
            saved_data = file.read().splitlines()
        self.assertEqual(saved_data, new_preferences)

class TestAPIKeys(unittest.TestCase):
    @patch("builtins.input", side_effect=["key1", "key2", "key3"])
    @patch("os.path.exists", return_value=False)
    @patch("api_keys.open")
    def test_load_api_keys_prompt(self, mock_open, mock_exists, mock_input):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        keys = load_api_keys()

        self.assertEqual(keys["Open Weather Map"], "key1")
        self.assertEqual(keys["Visual Crossing"], "key2")
        self.assertEqual(keys["Weather API"], "key3")

class TestErrorHandling(unittest.TestCase):
    @patch("fetch_weather.fetch_weather_openweathermap")
    def test_fetch_weather_openweathermap_error(self, mock_openweathermap):
        mock_openweathermap.side_effect = Exception("API error")
        result = fetch_weather_openweathermap("TestCity", "invalid_key")
        self.assertIsNone(result)

    @patch("fetch_weather.fetch_weather_visualcrossing")
    def test_fetch_weather_visualcrossing_error(self, mock_visualcrossing):
        mock_visualcrossing.side_effect = Exception("API error")
        result = fetch_weather_visualcrossing("TestCity", "invalid_key")
        self.assertIsNone(result)

    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_fetch_weather_weatherapi_error(self, mock_weatherapi):
        mock_weatherapi.side_effect = Exception("API error")
        result = fetch_weather_weatherapi("TestCity", "invalid_key")
        self.assertIsNone(result)

class TestIntegration(unittest.TestCase):
    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_full_integration(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 50}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 21,
                "tempmax": 26,
                "tempmin": 16,
                "humidity": 55,
                "aqi": 42,
                "sunrise": "6:00 AM",
                "sunset": "8:00 PM",
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 22, "humidity": 60}
        }

        preferences = ["CityA", "CityB"]

        for city in preferences:
            result = aggregate_weather_data(city, {
                "OpenWeatherMap": "dummy_key",
                "VisualCrossing": "dummy_key",
                "WeatherAPI": "dummy_key",
            })

            self.assertIsNotNone(result["avg_current_temp"])
            self.assertIsNotNone(result["avg_high_temp"])
            self.assertIsNotNone(result["avg_low_temp"])
            self.assertIsNotNone(result["avg_humidity"])

class TestAPIAndPreferencesIntegration(unittest.TestCase):
    @patch("api_keys.open")
    @patch("os.path.exists", return_value=True)
    @patch("csv.DictReader")
    def test_api_keys_integration(self, mock_csv_reader, mock_exists, mock_open):
        mock_csv_reader.return_value = [
            {"API": "Open Weather Map", "Key": "key1"},
            {"API": "Visual Crossing", "Key": "key2"},
            {"API": "Weather API", "Key": "key3"},
        ]

        keys = load_api_keys()
        self.assertEqual(keys["Open Weather Map"], "key1")
        self.assertEqual(keys["Visual Crossing"], "key2")
        self.assertEqual(keys["Weather API"], "key3")

    @patch("preferences.PREFERENCES_FILE", new_callable=lambda: "test_preferences.txt")
    def test_preferences_integration(self, mock_file):
        preferences = load_preferences()
        self.assertEqual(preferences, ["CityA", "CityB"])

        new_preferences = ["CityC", "CityD"]
        save_preferences(new_preferences)

        updated_preferences = load_preferences()
        self.assertEqual(updated_preferences, new_preferences)

class TestBoundaryConditions(unittest.TestCase):
    def setUp(self):
        self.city = "BoundaryCity"
        self.data_sources = {
            "OpenWeatherMap": "test_key_owm",
            "VisualCrossing": "test_key_vc",
            "WeatherAPI": "test_key_wa",
        }

    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_aggregate_weather_data_empty_response(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {}
        mock_visualcrossing.return_value = {}
        mock_weatherapi.return_value = {}

        result = aggregate_weather_data(self.city, self.data_sources)

        self.assertEqual(result["current_temp"], [])
        self.assertEqual(result["high_temp"], [])
        self.assertEqual(result["low_temp"], [])
        self.assertEqual(result["humidity"], [])
        self.assertIsNone(result["sunrise"])
        self.assertIsNone(result["sunset"])

    @patch("fetch_weather.fetch_weather_openweathermap")
    def test_aggregate_weather_data_single_source(self, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 0, "temp_max": 0, "temp_min": 0, "humidity": 0}
        }

        result = aggregate_weather_data(self.city, {"OpenWeatherMap": "test_key"})

        self.assertEqual(result["avg_current_temp"], 0)
        self.assertEqual(result["avg_high_temp"], 0)
        self.assertEqual(result["avg_low_temp"], 0)
        self.assertEqual(result["avg_humidity"], 0)

    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_aggregate_weather_data_extreme_values(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": -100, "temp_max": -50, "temp_min": -150, "humidity": 0}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 100,
                "tempmax": 120,
                "tempmin": 80,
                "humidity": 100,
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 50, "humidity": 50}
        }

        result = aggregate_weather_data(self.city, self.data_sources)

        self.assertEqual(result["avg_current_temp"], 17)  # Average of -100, 100, and 50
        self.assertEqual(result["avg_high_temp"], 23)  # Average of -50, 120, and 50
        self.assertEqual(result["avg_low_temp"], -7)  # Average of -150, 80, and 50
        self.assertEqual(result["avg_humidity"], 50)  # Average of 0, 100, and 50

class TestBoundaryCases(unittest.TestCase):
    def setUp(self):
        self.city = "EdgeCity"
        self.data_sources = {
            "OpenWeatherMap": "test_key_owm",
            "VisualCrossing": "test_key_vc",
            "WeatherAPI": "test_key_wa",
        }

    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_no_data_returned(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {}
        mock_visualcrossing.return_value = {}
        mock_weatherapi.return_value = {}

        result = aggregate_weather_data(self.city, self.data_sources)

        self.assertEqual(result["current_temp"], [])
        self.assertEqual(result["high_temp"], [])
        self.assertEqual(result["low_temp"], [])
        self.assertEqual(result["humidity"], [])
        self.assertIsNone(result["sunrise"])
        self.assertIsNone(result["sunset"])

    @patch("fetch_weather.fetch_weather_openweathermap")
    def test_single_source_partial_data(self, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 25, "temp_max": 30, "temp_min": 20, "humidity": 40}
        }

        result = aggregate_weather_data(self.city, {"OpenWeatherMap": "test_key"})

        self.assertEqual(result["avg_current_temp"], 25)
        self.assertEqual(result["avg_high_temp"], 30)
        self.assertEqual(result["avg_low_temp"], 20)
        self.assertEqual(result["avg_humidity"], 40)

    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_extreme_temperature_values(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": -100, "temp_max": -50, "temp_min": -150, "humidity": 0}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 100,
                "tempmax": 120,
                "tempmin": 80,
                "humidity": 100,
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 50, "humidity": 50}
        }

        result = aggregate_weather_data(self.city, self.data_sources)

        self.assertEqual(result["avg_current_temp"], 17)
        self.assertEqual(result["avg_high_temp"], 23)
        self.assertEqual(result["avg_low_temp"], -7)
        self.assertEqual(result["avg_humidity"], 50)

    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_conflicting_aqi_values(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 45}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 21,
                "tempmax": 26,
                "tempmin": 16,
                "humidity": 50,
                "aqi": 75,
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 22, "humidity": 55}
        }

        result = aggregate_weather_data(self.city, self.data_sources)

        self.assertIn(75, result["aqi"])
        self.assertEqual(result["avg_current_temp"], 21)
        self.assertEqual(result["avg_high_temp"], 26)
        self.assertEqual(result["avg_low_temp"], 16)
        self.assertEqual(result["avg_humidity"], 50)

class TestWeatherAggregator(unittest.TestCase):
    def setUp(self):
        self.city = "TestCity"
        self.data_sources = {
            "OpenWeatherMap": "test_openweathermap_key",
            "VisualCrossing": "test_visualcrossing_key",
            "WeatherAPI": "test_weatherapi_key",
        }

    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_aggregate_weather_data(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 50}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 21,
                "tempmax": 26,
                "tempmin": 16,
                "humidity": 55,
                "aqi": 42,
                "sunrise": "6:00 AM",
                "sunset": "8:00 PM",
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 22, "humidity": 60}
        }

        result = aggregate_weather_data(self.city, self.data_sources)

        self.assertEqual(result["avg_current_temp"], 21)
        self.assertEqual(result["avg_high_temp"], 26)
        self.assertEqual(result["avg_low_temp"], 16)
        self.assertEqual(result["avg_humidity"], 55)
        self.assertIn(42, result["aqi"])
        self.assertEqual(result["sunrise"], "6:00 AM")
        self.assertEqual(result["sunset"], "8:00 PM")

    @patch("fetch_weather.fetch_weather_openweathermap")
    def test_aggregate_weather_data_with_missing_source(self, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 50}
        }

        incomplete_sources = {
            "OpenWeatherMap": "test_openweathermap_key",
        }

        result = aggregate_weather_data(self.city, incomplete_sources)

        self.assertEqual(result["avg_current_temp"], 20)
        self.assertEqual(result["avg_high_temp"], 25)
        self.assertEqual(result["avg_low_temp"], 15)
        self.assertEqual(result["avg_humidity"], 50)

class TestPreferences(unittest.TestCase):
    def setUp(self):
        self.preferences_file = "test_preferences.txt"
        self.sample_preferences = ["CityA", "CityB"]
        with open(self.preferences_file, "w") as file:
            file.write("\n".join(self.sample_preferences))

    def tearDown(self):
        import os

        if os.path.exists(self.preferences_file):
            os.remove(self.preferences_file)

    @patch("preferences.PREFERENCES_FILE", new_callable=lambda: "test_preferences.txt")
    def test_load_preferences(self, mock_file):
        preferences = load_preferences()
        self.assertEqual(preferences, self.sample_preferences)

    @patch("preferences.PREFERENCES_FILE", new_callable=lambda: "test_preferences.txt")
    def test_save_preferences(self, mock_file):
        new_preferences = ["CityX", "CityY"]
        save_preferences(new_preferences)
        with open(self.preferences_file, "r") as file:
            saved_data = file.read().splitlines()
        self.assertEqual(saved_data, new_preferences)

class TestAPIKeys(unittest.TestCase):
    @patch("builtins.input", side_effect=["key1", "key2", "key3"])
    @patch("os.path.exists", return_value=False)
    @patch("api_keys.open")
    def test_load_api_keys_prompt(self, mock_open, mock_exists, mock_input):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        keys = load_api_keys()

        self.assertEqual(keys["Open Weather Map"], "key1")
        self.assertEqual(keys["Visual Crossing"], "key2")
        self.assertEqual(keys["Weather API"], "key3")

class TestErrorHandling(unittest.TestCase):
    @patch("fetch_weather.fetch_weather_openweathermap")
    def test_fetch_weather_openweathermap_error(self, mock_openweathermap):
        mock_openweathermap.side_effect = Exception("API error")
        result = fetch_weather_openweathermap("TestCity", "invalid_key")
        self.assertIsNone(result)

    @patch("fetch_weather.fetch_weather_visualcrossing")
    def test_fetch_weather_visualcrossing_error(self, mock_visualcrossing):
        mock_visualcrossing.side_effect = Exception("API error")
        result = fetch_weather_visualcrossing("TestCity", "invalid_key")
        self.assertIsNone(result)

    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_fetch_weather_weatherapi_error(self, mock_weatherapi):
        mock_weatherapi.side_effect = Exception("API error")
        result = fetch_weather_weatherapi("TestCity", "invalid_key")
        self.assertIsNone(result)

class TestIntegration(unittest.TestCase):
    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_full_integration(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 50}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 21,
                "tempmax": 26,
                "tempmin": 16,
                "humidity": 55,
                "aqi": 42,
                "sunrise": "6:00 AM",
                "sunset": "8:00 PM",
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 22, "humidity": 60}
        }

        preferences = ["CityA", "CityB"]

        for city in preferences:
            result = aggregate_weather_data(city, {
                "OpenWeatherMap": "dummy_key",
                "VisualCrossing": "dummy_key",
                "WeatherAPI": "dummy_key",
            })

            self.assertIsNotNone(result["avg_current_temp"])
            self.assertIsNotNone(result["avg_high_temp"])
            self.assertIsNotNone(result["avg_low_temp"])
            self.assertIsNotNone(result["avg_humidity"])

class TestStressTesting(unittest.TestCase):
    @patch("fetch_weather.fetch_weather_openweathermap")
    @patch("fetch_weather.fetch_weather_visualcrossing")
    @patch("fetch_weather.fetch_weather_weatherapi")
    def test_large_number_of_cities(self, mock_weatherapi, mock_visualcrossing, mock_openweathermap):
        mock_openweathermap.return_value = {
            "main": {"temp": 20, "temp_max": 25, "temp_min": 15, "humidity": 50}
        }
        mock_visualcrossing.return_value = {
            "currentConditions": {
                "temp": 21,
                "tempmax": 26,
                "tempmin": 16,
                "humidity": 55,
                "aqi": 42,
                "sunrise": "6:00 AM",
                "sunset": "8:00 PM",
            }
        }
        mock_weatherapi.return_value = {
            "current": {"temp_c": 22, "humidity": 60}
        }

        cities = [f"City{i}" for i in range(100)]
        for city in cities:
            result = aggregate_weather_data(city, {
                "OpenWeatherMap": "dummy_key",
                "VisualCrossing": "dummy_key",
                "WeatherAPI": "dummy_key",
            })

            self.assertIsNotNone(result["avg_current_temp"])
            self.assertIsNotNone(result["avg_high_temp"])
            self.assertIsNotNone(result["avg_low_temp"])
            self.assertIsNotNone(result["avg_humidity"])

if __name__ == "__main__":
    unittest.main()
